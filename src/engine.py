"""Instruction execution engine and main simulation loop (v3).

Implements project-report.md section 1a. Notable points:
  - MOV destination is a literal register index (report 4e)
  - COPY_BLOCK copies n instructions (n from R6) in one tick, cost 2 + n/64,
    with substitution mutation applied per instruction copied
  - memory is returned to the shared pool exactly once, via the corpse pool
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from consts import *
from organism import Organism, Substrate


def efficiency_assay_genome(
        extent: int, tau_r5: int = 51,
        offspring_bouts: int = 2) -> list[tuple]:
    """Build an efficiency treatment genome with fresh work per offspring."""
    if offspring_bouts < 1:
        raise ValueError("offspring_bouts must be positive")
    length = 8 + 3 * offspring_bouts
    result = [
        (MOV, 5, tau_r5),
        (MOV, 6, length),
        (MOV, 0, PACKET_SIZE),
        (ALLOC, 0),
        (READ, 1, PACKET_SIZE),
        (TRANSFORM, TRANSFORM_RLE, 1, extent),
        (FREE, 1),
    ]
    for _ in range(offspring_bouts):
        result.extend([
            (ALLOC_OFFSPRING, MIN_WORKING_MEMORY),
            (COPY_BLOCK,),
            (DIVIDE,),
        ])
    result.append((JUMP, 2))
    if len(result) != length:
        raise AssertionError("efficiency genome length mismatch")
    return result


def conditional_efficiency_assay_genome(
        extent: int, tau_r5: int = 51) -> list[tuple]:
    """Equal-tempo p=1 test: FULL executes a third bout, HALF pads it."""
    length = 23
    result = [
        (MOV, 5, tau_r5),
        (MOV, 6, length),
        (MOV, 0, PACKET_SIZE),
        (ALLOC, 0),
        (READ, 1, PACKET_SIZE),
        (TRANSFORM, TRANSFORM_RLE, 1, extent),
        (FREE, 1),
    ]
    for _ in range(2):
        result.extend([
            (ALLOC_OFFSPRING, MIN_WORKING_MEMORY),
            (COPY_BLOCK,),
            (DIVIDE,),
        ])
    result.extend([
        (AND, 7, 4, 2048),      # bit 11: FULL R4 set, HALF R4 clear
        (JUMPZ, 7, 19),         # HALF takes equal-tempo padding path
        (ALLOC_OFFSPRING, MIN_WORKING_MEMORY),
        (COPY_BLOCK,),
        (DIVIDE,),
        (JUMP, 2),
        (NOP,),
        (NOP,),
        (NOP,),
        (JUMP, 2),
    ])
    if len(result) != length:
        raise AssertionError("conditional efficiency genome length mismatch")
    return result


class InstructionEngine:
    """Executes one instruction for one organism per tick."""

    def __init__(self, substrate: Substrate):
        self.substrate = substrate

    # ------------------------------------------------------------------
    # Cost accounting
    # ------------------------------------------------------------------

    def _instruction_cost(self, org: Organism, opcode: int, args: tuple) -> float:
        base = INSTRUCTION_COST.get(opcode, 1)
        extra = 0
        if opcode == ALLOC:
            size = self._get_reg(org, args[0] if args else 0, MIN_WORKING_MEMORY)
            extra = max(0, (size + 63) // 64)
        elif opcode == ALLOC_OFFSPRING:
            size = self._get_reg(org, args[0] if args else 0, MIN_WORKING_MEMORY)
            if size <= 0:
                size = MIN_WORKING_MEMORY
            extra = max(0, (size + 63) // 64)
        elif opcode == TRANSFORM:
            length = self._get_reg(org, args[2] if len(args) > 2 else 0, 64)
            extra = max(1, (length + 63) // 64)
        elif opcode == COPY_BLOCK:
            n = self._block_length(org)
            extra = max(0, (n + 63) // 64)
        return base + extra

    def _block_length(self, org: Organism) -> int:
        """Number of instructions COPY_BLOCK will attempt to copy this tick."""
        n = org.registers[6]
        if not isinstance(n, int) or n <= 0:
            n = org.genome_length
        remaining = max(0, org.genome_length - org.copy_pointer)
        return min(n, remaining)

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def execute(self, org: Organism) -> bool:
        if org.state != "ACTIVE":
            return org.state != "DEAD"
        org.last_execution_tick = self.substrate.tick
        if org.pc < 0 or org.pc >= org.genome_length:
            self.substrate.remove_organism(org.id, "PC out of bounds")
            return False

        instr = org.genome[org.pc]
        opcode = instr[0]
        args = instr[1:]
        total_cost = self._instruction_cost(org, opcode, args)

        alive = self._execute_instr(org, opcode, args)

        # Cost is paid whether or not the instruction succeeded.
        org.execution_reserve -= total_cost
        if org.state == "DEAD":
            self.substrate.refresh_terminal_reserve(org)
            return False
        if org.execution_reserve <= 0:
            self.substrate.remove_organism(org.id, "reserve exhausted")
            return False
        if not alive:
            return org.state != "DEAD"

        if opcode not in (JUMP, JUMPZ, JUMPNZ):
            org.pc += 1
            if org.pc >= org.genome_length:
                self.substrate.remove_organism(org.id, "PC past end of genome")
                return False

        if opcode == SLEEP:
            org.state = "DORMANT"
        return True

    def _get_reg(self, org: Organism, arg, default=0) -> int:
        """Registers 0-7 are read as registers; larger integers are literals."""
        if isinstance(arg, int) and 0 <= arg <= 7:
            return org.registers[arg]
        return arg if isinstance(arg, int) else default

    def _execute_instr(self, org: Organism, opcode: int, args: tuple) -> bool:
        rng = self.substrate.rng

        if opcode == NOP:
            pass

        elif opcode == JUMP:
            target = args[0] if args else 0
            org.pc = target if 0 <= target < org.genome_length else 0

        elif opcode == JUMPZ:
            reg = self._get_reg(org, args[0] if args else 0, 0)
            target = args[1] if len(args) > 1 else 0
            if reg == 0 and 0 <= target < org.genome_length:
                org.pc = target
            else:
                org.pc += 1

        elif opcode == JUMPNZ:
            reg = self._get_reg(org, args[0] if args else 0, 0)
            target = args[1] if len(args) > 1 else 0
            if reg != 0 and 0 <= target < org.genome_length:
                org.pc = target
            else:
                org.pc += 1

        elif opcode == MOV:
            # Destination is a literal register index (report 4e).
            dst = args[0] if args else 0
            src = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            if isinstance(dst, int) and 0 <= dst <= 7:
                org.registers[dst] = src
            else:
                org.fail_flag = True

        elif opcode in (ADD, SUB):
            dst = args[0] if args else 0
            a = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            b = self._get_reg(org, args[2] if len(args) > 2 else 0, 0)
            if isinstance(dst, int) and 0 <= dst <= 7:
                result = a + b if opcode == ADD else a - b
                org.registers[dst] = result & 0xFFFFFFFF
                org.carry_flag = result > 0xFFFFFFFF if opcode == ADD else result < 0

        elif opcode in (AND, OR, XOR):
            dst = args[0] if args else 0
            a = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            b = self._get_reg(org, args[2] if len(args) > 2 else 0, 0)
            if isinstance(dst, int) and 0 <= dst <= 7:
                if opcode == AND:
                    org.registers[dst] = a & b
                elif opcode == OR:
                    org.registers[dst] = a | b
                else:
                    org.registers[dst] = a ^ b

        elif opcode == CMP:
            a = self._get_reg(org, args[0] if args else 0, 0)
            b = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            org.carry_flag = (a == b)

        elif opcode == READ:
            addr = self._get_reg(org, args[0] if args else 0, 0)
            length = self._get_reg(org, args[1] if len(args) > 1 else 0, PACKET_SIZE)
            self.substrate.read_packet(org, addr, length)

        elif opcode == WRITE:
            pass

        elif opcode == ALLOC:
            size = self._get_reg(org, args[0] if args else 0, MIN_WORKING_MEMORY)
            addr = org.allocate_memory(size)
            if addr is not None:
                org.registers[1] = addr
                org.fail_flag = False
            else:
                org.fail_flag = True

        elif opcode == FREE:
            addr = self._get_reg(org, args[0] if args else 0, 0)
            org.fail_flag = not org.free_memory(addr)

        elif opcode == TRANSFORM:
            op = args[0] if args else 0          # literal transform opcode
            addr = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            length = self._get_reg(org, args[2] if len(args) > 2 else 0, 64)
            # Log the resolved execution, not the mutable ancestry label or
            # raw operand. Register-indirect mutations can change the realised
            # extent without changing the ancestral treatment assignment.
            org.last_transform_op = op
            org.last_transform_extent = length
            org.last_transform_tick = self.substrate.tick
            key = (op, length)
            org.transform_execution_counts[key] = \
                org.transform_execution_counts.get(key, 0) + 1
            self.substrate.apply_transform(org, op, addr, length)

        elif opcode == SLEEP:
            ticks = self._get_reg(org, args[0] if args else 0, 100)
            org.sleep_remaining = max(1, ticks)

        elif opcode == DIE:
            self.substrate.remove_organism(org.id, "voluntary DIE")
            return False

        elif opcode == ALLOC_OFFSPRING:
            size = self._get_reg(org, args[0] if args else 0, MIN_WORKING_MEMORY)
            if size <= 0:
                size = MIN_WORKING_MEMORY
            # Free previous gestation region if it exists
            if org.gestation_region is not None and org.gestation_region in org.memory_allocations:
                old_size = org.memory_allocations.pop(org.gestation_region)
                if org.substrate is not None:
                    org.substrate.shared_memory_pool += old_size
            # The old bout is invalid once replacement begins, even if the
            # new allocation fails. Never leave a stale copied genome usable
            # by a later DIVIDE.
            org.gestation_region = None
            org.gestation_size = 0
            org.copy_pointer = 0
            org.gestation_buffer = []
            org.registers[2] = 0
            addr = org.allocate_memory(size)
            if addr is None:
                org.fail_flag = True
            else:
                org.gestation_region = addr
                org.gestation_size = size
                # Reproduction bout boundary: reset the per-cycle DIVIDE counter.
                org.divides_last_cycle = org.divides_this_cycle
                org.divides_this_cycle = 0
                org.fail_flag = False

        elif opcode == COPY_UNIT:
            if org.gestation_region is None:
                org.fail_flag = True
            elif org.copy_pointer >= org.genome_length:
                org.registers[2] = 1
                org.fail_flag = False
            else:
                org.gestation_buffer.append(
                    self._copy_one(org, org.genome[org.copy_pointer], rng))
                org.copy_pointer += 1
                org.registers[2] = 1 if org.copy_pointer >= org.genome_length else 0
                org.fail_flag = False

        elif opcode == COPY_BLOCK:
            if org.gestation_region is None:
                org.fail_flag = True
            else:
                n = self._block_length(org)
                for _ in range(n):
                    org.gestation_buffer.append(
                        self._copy_one(org, org.genome[org.copy_pointer], rng))
                    org.copy_pointer += 1
                org.registers[2] = 1 if org.copy_pointer >= org.genome_length else 0
                org.fail_flag = (n == 0 and org.copy_pointer < org.genome_length)

        elif opcode == DIVIDE:
            org.divide_attempts += 1
            reserve_before = org.execution_reserve
            offspring_id = self.substrate.reproduce(org)
            divide_event = {
                "tick": self.substrate.tick,
                "parent_id": org.id,
                "lineage_label": org.lineage_label,
                "founder_lineage_id": org.founder_lineage_id,
                "resolved_transform_op": org.last_transform_op,
                "resolved_transform_extent": org.last_transform_extent,
                "attempt_number": org.divide_attempts,
                "offspring_instantiated": offspring_id is not None,
                "materialization_failure_reason": (
                    org.last_reproduction_failure_reason
                ),
                "offspring_id": offspring_id,
                "reserve_before_transfer": reserve_before,
                "reserve_after_transfer": org.execution_reserve,
            }
            # A transfer exists only when an offspring exists to receive it.
            # Failed materialisation retains reserve snapshots but has no
            # transfer_reserve field.
            if offspring_id is not None:
                divide_event["transfer_reserve"] = max(
                    0.0, reserve_before - org.execution_reserve)
            self.substrate.divide_event_log.append(divide_event)
            if offspring_id is None:
                org.fail_flag = True

        elif opcode == SET_P:
            val = self._get_reg(org, args[0] if args else 0, 0)
            org.copy_pointer = max(0, min(val, org.genome_length))
            org.registers[2] = 1 if org.copy_pointer >= org.genome_length else 0

        elif opcode == READ_GESTATION:
            dst = args[0] if args else 0
            offset = self._get_reg(org, args[1] if len(args) > 1 else 0, 0)
            if isinstance(dst, int) and 0 <= dst <= 7 and \
                    0 <= offset < len(org.gestation_buffer):
                org.registers[dst] = org.gestation_buffer[offset][0]
                org.fail_flag = False
            else:
                org.fail_flag = True

        return True

    def _copy_one(self, org: Organism, instr: tuple, rng) -> tuple:
        """Copy one instruction, applying substitution mutation per instruction.

        Mutation is per instruction copied, not per invocation, so copy
        fidelity is neutral with respect to COPY_BLOCK's block size.
        """
        if rng.random() < MUTATION_SUBSTITUTION:
            new_op = rng.randint(0, MAX_OPCODE)
            new_args = tuple(rng.randint(0, 255) for _ in range(max(0, len(instr) - 1)))
            return (new_op,) + new_args
        return instr


class Simulation:
    """Main simulation loop (v3)."""

    def __init__(self, seed: int = 42, phase_mode: str = 'long',
                 packet_e_rich: float = PACKET_E_RICH,
                 packet_e_lean: float = PACKET_E_LEAN,
                 packet_rate: int = PACKET_RATE,
                 buffer_depth: int = BUFFER_DEPTH,
                 population_cap: int = POPULATION_CAP,
                 initial_buffer_packets: int = 0,
                 offspring_maturation_delay: int = 0):
        self.substrate = Substrate(
            seed, phase_mode, packet_e_rich, packet_e_lean,
            packet_rate=packet_rate, buffer_depth=buffer_depth,
            population_cap=population_cap,
            initial_buffer_packets=initial_buffer_packets,
            offspring_maturation_delay=offspring_maturation_delay)
        self.engine = InstructionEngine(self.substrate)
        self.tick = 0
        self.metrics = {
            "births": 0, "deaths": 0,
            "max_population": 0, "max_generation": 0,
            "extinct_tick": None,
        }

    def realised_parameters(self) -> dict:
        """Read experiment parameters back from the live runtime objects."""
        packet_buffer = self.substrate.data_stream
        stream = packet_buffer.stream
        return {
            "seed": self.substrate.seed,
            "phase_mode": stream.phase_mode,
            "packet_e_rich": stream.packet_e_rich,
            "packet_e_lean": stream.packet_e_lean,
            "packet_rate": packet_buffer.packet_rate,
            "buffer_depth": packet_buffer.max_depth,
            "initial_buffer_packets": packet_buffer.initial_buffer_packets,
            "population_cap": self.substrate.population_cap,
            "cap_victim_sampling":
                "uniform_all_incumbents_including_parent",
            "offspring_viability_gate": "none",
            "offspring_maturation_delay":
                self.substrate.offspring_maturation_delay,
            "minimum_working_memory": MIN_WORKING_MEMORY,
            "shared_memory_pool_initial":
                self.substrate.initial_shared_memory_pool,
            "shared_memory_pool_current":
                self.substrate.shared_memory_pool,
            "memory_allocation_failures_total":
                self.substrate.memory_allocation_failures_total,
        }

    def realised_parameter_header(self) -> str:
        """Stable, machine-readable header for saved experimental output."""
        values = self.realised_parameters()
        return "PARAMETERS " + " ".join(
            f"{key}={values[key]}" for key in sorted(values))

    def realised_memory_capacity(self, peak_bytes_per_organism: int) -> dict:
        """Read back pool size and derive a conservative synchronous ceiling."""
        peak = int(peak_bytes_per_organism)
        if peak <= 0:
            raise ValueError("peak_bytes_per_organism must be positive")
        pool = self.substrate.initial_shared_memory_pool
        return {
            "memory_pool_bytes": pool,
            "peak_bytes_per_organism": peak,
            "synchronous_peak_population_ceiling": pool // peak,
        }

    def realised_memory_capacity_header(
            self, peak_bytes_per_organism: int) -> str:
        values = self.realised_memory_capacity(peak_bytes_per_organism)
        return "MEMORY_CAPACITY " + " ".join(
            f"{key}={values[key]}" for key in sorted(values))

    # ------------------------------------------------------------------
    # Seed genomes
    # ------------------------------------------------------------------

    def seed_efficiency_assay_founders(
            self, full_count: int = 78, half_count: int = 77,
            tau_r5: int = 51, offspring_bouts: int = 2) -> list[int]:
        """Seed the direct-cap FULL/HALF efficiency assay treatment."""
        if self.substrate.organisms:
            raise ValueError("efficiency assay requires an empty substrate")
        if full_count + half_count != self.substrate.population_cap:
            raise ValueError("founder total must equal the live population cap")
        if offspring_bouts < 1:
            raise ValueError("offspring_bouts must be positive")

        ids = []
        remaining = {"FULL": int(full_count), "HALF": int(half_count)}
        while remaining["FULL"] or remaining["HALF"]:
            for label, extent in (("FULL", 256), ("HALF", 128)):
                if remaining[label] <= 0:
                    continue
                org = self.substrate.add_organism(
                    efficiency_assay_genome(
                        extent, tau_r5, offspring_bouts),
                    lineage_label=label)
                if org is None:
                    raise RuntimeError("failed to allocate assay founder")
                ids.append(org.id)
                remaining[label] -= 1
        return ids

    def seed_m1(self, tau_r5: int = DEFAULT_TRANSFER_R5, transform_op: int = TRANSFORM_RLE):
        """Reference metaboliser M1 (L=11): forage, transform, copy, divide."""
        genome = [
            (MOV, 5, tau_r5),                 # 0: R5 = tau numerator
            (MOV, 0, PACKET_SIZE),            # 1: R0 = 256
            (ALLOC, 0),                       # 2: ALLOC R0 -> R1 = buffer addr
            (READ, 1, PACKET_SIZE),           # 3: READ into R1
            (TRANSFORM, transform_op, 1, PACKET_SIZE),  # 4: TRANSFORM at R1
            (FREE, 1),                        # 5: FREE buffer
            (ALLOC_OFFSPRING, 64),            # 6: gestation region
            (COPY_UNIT,),                     # 7: copy loop
            (JUMPZ, 2, 7),                    # 8: while R2 == 0, copy again
            (DIVIDE,),                        # 9: DIVIDE
            (JUMP, 1),                        # 10: next cycle
        ]
        return self.substrate.add_organism(genome)

    def seed_m1_block(self, tau_r5: int = 51, transform_op: int = TRANSFORM_RLE):
        """Processive metaboliser: COPY_BLOCK replaces the copy loop.

        R6 holds the block length. Multiple DIVIDEs per cycle are possible
        because the parent retains 1 - tau of its reserve after each.
        """
        genome = [
            (MOV, 5, tau_r5),                 # 0: tau numerator
            (MOV, 6, 32),                     # 1: R6 = block length
            (MOV, 0, PACKET_SIZE),            # 2: R0 = 256
            (ALLOC, 0),                       # 3: ALLOC -> R1
            (READ, 1, PACKET_SIZE),           # 4: READ
            (TRANSFORM, transform_op, 1, PACKET_SIZE),  # 5: TRANSFORM
            (FREE, 1),                        # 6: FREE
            (ALLOC_OFFSPRING, 64),            # 7: gestation
            (COPY_BLOCK,),                    # 8: copy whole genome in 1 tick
            (JUMPZ, 2, 8),                    # 9: repeat if not finished
            (DIVIDE,),                        # 10: DIVIDE
            (JUMP, 2),                        # 11: next cycle
        ]
        return self.substrate.add_organism(genome)

    def seed_switcher(self, tau_r5: int = 51):
        """Probes RLE; if no reduction (R3 == 0), falls through to DIFF."""
        genome = [
            (MOV, 5, tau_r5),                 # 0
            (MOV, 6, 32),                     # 1
            (MOV, 0, PACKET_SIZE),            # 2
            (ALLOC, 0),                       # 3
            (READ, 1, PACKET_SIZE),           # 4
            (TRANSFORM, TRANSFORM_RLE, 1, PACKET_SIZE),   # 5: probe
            (JUMPNZ, 3, 8),                   # 6: R3 != 0 -> RLE worked
            (TRANSFORM, TRANSFORM_DIFF, 1, PACKET_SIZE),  # 7: fallback
            (FREE, 1),                        # 8
            (ALLOC_OFFSPRING, 64),            # 9
            (COPY_BLOCK,),                    # 10
            (JUMPZ, 2, 10),                   # 11
            (DIVIDE,),                        # 12
            (JUMP, 2),                        # 13
        ]
        return self.substrate.add_organism(genome)

    def seed_bare_replicator(self):
        """Minimal replicator (no metabolism). Has no income and dies."""
        genome = [
            (ALLOC_OFFSPRING, 64),
            (COPY_UNIT,),
            (JUMPZ, 2, 1),
            (DIVIDE,),
            (JUMP, 0),
        ]
        return self.substrate.add_organism(genome)

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def step(self) -> int:
        self.substrate.tick = self.tick
        self.substrate.capture_attempts_tick = 0
        self.substrate.capture_successes_tick = 0
        self.substrate.data_stream.advance_tick()

        # Reap the dead. remove_organism() already released their memory to
        # the corpse pool; releasing again here would double-count.
        for oid in [oid for oid, o in self.substrate.organisms.items()
                    if o.state == "DEAD"]:
            del self.substrate.organisms[oid]

        maturing_ids_at_tick_start = {
            oid for oid, o in self.substrate.organisms.items()
            if o.state == "ACTIVE" and o.maturation_remaining > 0
        }
        active_ids = [oid for oid, o in self.substrate.organisms.items()
                      if o.state == "ACTIVE" and
                      o.maturation_remaining <= 0]
        self.substrate.rng.shuffle(active_ids)
        for oid in active_ids:
            org = self.substrate.organisms.get(oid)
            if org is None or org.state != "ACTIVE":
                continue
            self.engine.execute(org)

        # Maturation blocks instruction execution only. Maturing offspring
        # remain ACTIVE, retain memory, and pay full upkeep below.
        for oid in maturing_ids_at_tick_start:
            org = self.substrate.organisms.get(oid)
            if (org is not None and org.state == "ACTIVE" and
                    org.maturation_remaining > 0):
                org.maturation_remaining -= 1

        for org in list(self.substrate.organisms.values()):
            if org.state == "DORMANT":
                org.sleep_remaining -= 1
                if org.sleep_remaining <= 0:
                    org.state = "ACTIVE"
                    org.sleep_woke_flag = True

        for org in list(self.substrate.organisms.values()):
            if org.state in ("ACTIVE", "DORMANT"):
                org.execution_reserve -= org.compute_upkeep()
                if org.execution_reserve <= 0:
                    self.substrate.remove_organism(org.id, "reserve exhausted")

        # Corpse memory returns to the shared pool once, on expiry.
        self.substrate.expire_corpse_memory()

        pop = sum(1 for o in self.substrate.organisms.values() if o.state != "DEAD")
        attempts = self.substrate.capture_attempts_tick
        successes = self.substrate.capture_successes_tick
        self.substrate.capture_history.append({
            "tick": self.tick,
            "population": pop,
            "maturing_population": sum(
                1 for o in self.substrate.organisms.values()
                if o.state != "DEAD" and o.maturation_remaining > 0),
            "buffer_occupancy": len(self.substrate.data_stream.buffer),
            "shared_memory_pool": self.substrate.shared_memory_pool,
            "committed_memory":
                (self.substrate.initial_shared_memory_pool -
                 self.substrate.shared_memory_pool),
            "memory_allocation_failures_total":
                self.substrate.memory_allocation_failures_total,
            "valid_read_attempts": attempts,
            "capture_successes": successes,
            "capture_fraction": (successes / attempts
                                 if attempts else None),
        })
        self.metrics["max_population"] = max(self.metrics["max_population"], pop)
        for org in self.substrate.organisms.values():
            if org.generation > self.metrics["max_generation"]:
                self.metrics["max_generation"] = org.generation

        self.tick += 1
        if pop == 0 and self.metrics["extinct_tick"] is None:
            self.metrics["extinct_tick"] = self.tick - 1
        return pop

    def run(self, max_ticks: int = 50000) -> dict:
        for _ in range(max_ticks):
            if self.step() == 0:
                break
        self.metrics["ticks"] = self.tick
        self.metrics["births"] = self.substrate.births
        self.metrics["deaths"] = self.substrate.deaths
        return self.metrics

    # ------------------------------------------------------------------
    # Instrumentation
    # ------------------------------------------------------------------

    def divide_stats(self) -> dict:
        """Per-cycle DIVIDE counts, split by whether the organism reproduced."""
        living = [o for o in self.substrate.organisms.values() if o.state != "DEAD"]
        if not living:
            return {"n": 0}
        counts = [o.divides_last_cycle or o.divides_this_cycle for o in living]
        reproducers = [c for c in counts if c > 0]
        return {
            "n": len(living),
            "k_mean_population": sum(counts) / len(counts),
            "n_reproducers": len(reproducers),
            "fraction_reproducing": len(reproducers) / len(living),
            "k_mean_reproducers": (sum(reproducers) / len(reproducers)
                                   if reproducers else 0.0),
        }


if __name__ == "__main__":
    sim = Simulation(seed=42, phase_mode='long')
    print(sim.realised_parameter_header())
    org = sim.seed_m1_block(tau_r5=51)
    print(f"Seeded M1-block (L={org.genome_length}), "
          f"reserve={org.execution_reserve:.0f}, pool={sim.substrate.shared_memory_pool}")
    for t in range(2000):
        pop = sim.step()
        if t % 250 == 0:
            s = sim.divide_stats()
            print(f"  tick {t:>5}: pop={pop:>4} gen={sim.metrics['max_generation']:>3} "
                  f"k_repro={s.get('k_mean_reproducers', 0):.2f} "
                  f"frac_repro={s.get('fraction_reproducing', 0):.2f} "
                  f"pool={sim.substrate.shared_memory_pool}")
        if pop == 0:
            print(f"  EXTINCT at tick {t}")
            break
    print(f"Done: ticks={sim.tick}, max_pop={sim.metrics['max_population']}, "
          f"max_gen={sim.metrics['max_generation']}, "
          f"instantiated_offspring={sim.substrate.births}")