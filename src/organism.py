"""Organism VM and Substrate (v3).

Implements project-report.md sections 1a-1d:
  - packet-ID-tagged memory with a closed per-packet energy budget
  - signed extraction gated on can_reconstruct() (losslessness)
  - expansion charge capped by the amount previously drawn from that packet
  - expansion leaves the original data intact
  - heritable transfer fraction tau = R5/256, no clamp
  - every materially allocatable offspring is instantiated with its transfer;
    viability emerges from ordinary execution and upkeep
  - memory returned to the shared pool exactly once, via the corpse pool
"""

import random
from consts import *
from transforms import compute_transform, can_reconstruct
from datastream import Packet, PacketBuffer


class Organism:
    """A single digital organism with packet-ID-tagged memory."""

    def __init__(self, genome: list[tuple], organism_id: int,
                 execution_reserve: float = INITIAL_EXECUTION_RESERVE,
                 parent_id: int = -1, generation: int = 0,
                 substrate=None, lineage_label: str | None = None,
                 founder_lineage_id: int | None = None):
        self.id = organism_id
        self.parent_id = parent_id
        self.generation = generation
        # Measurement-only ancestry label. It is inherited unchanged and must
        # not be used as a phenotype classifier.
        self.lineage_label = lineage_label
        self.founder_lineage_id = founder_lineage_id
        self.genome = genome
        self.genome_length = len(genome)
        self.registers = [0] * 8
        self.pc = 0
        self.stack = []
        self.working_memory = bytearray(MIN_WORKING_MEMORY)
        # Per-byte packet ID tags: None for internal, int for packet-sourced.
        # Tags propagate on copy, so duplicating bytes cannot create budget.
        self.byte_tags: list[int | None] = [None] * MIN_WORKING_MEMORY
        self.packet_energy: dict[int, float] = {}   # packet_id -> remaining budget
        self.packet_drawn: dict[int, float] = {}    # packet_id -> total drawn so far
        self.packet_metadata: dict[int, tuple[int, int]] = {}  # pid -> (max_reducible, S)
        self.gestation_region: int | None = None
        self.gestation_size: int = 0
        self.gestation_buffer: list[tuple] = []
        self.copy_pointer: int = 0
        self.persistent_store = bytearray(0)
        self.execution_reserve = execution_reserve
        self.state = "ACTIVE"
        self.sleep_remaining = 0
        self.carry_flag = False
        self.fail_flag = False
        self.last_execution_tick: int | None = None
        self.last_valid_read_tick: int | None = None
        self.maturation_remaining = 0
        self.sleep_woke_flag = False
        self.death_cause = ""
        self.memory_allocations = {0: MIN_WORKING_MEMORY}
        self.substrate = substrate
        # Instrumentation (measurement only; no effect on dynamics)
        self.divides_this_cycle = 0   # reset on ALLOC_OFFSPRING
        self.divides_last_cycle = 0
        self.total_divides = 0
        self.divide_attempts = 0
        self.first_divide_tick: int | None = None
        self.last_reproduction_failure_reason: str | None = None
        self.birth_tick = substrate.tick if substrate is not None else 0
        self.last_transform_op: int | None = None
        self.last_transform_extent: int | None = None
        self.last_transform_tick: int | None = None
        self.first_positive_extraction_tick: int | None = None
        self.transform_execution_counts: dict[tuple[int, int], int] = {}

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def get_working_memory_size(self) -> int:
        return sum(self.memory_allocations.values())

    def is_memory_range_valid(self, addr: int, length: int) -> bool:
        if addr < 0 or length < 0:
            return False
        for base, size in self.memory_allocations.items():
            if base <= addr < base + size:
                return base <= (addr + length - 1) < base + size
        return False

    def allocate_memory(self, size: int) -> int | None:
        """Allocate from the shared pool. Returns base address or None."""
        if size <= 0:
            return None
        if self.substrate is not None:
            if self.substrate.shared_memory_pool < size:
                self.substrate.memory_allocation_failures_total += 1
                return None
            self.substrate.shared_memory_pool -= size
        highest_end = max(a + s for a, s in self.memory_allocations.items()) \
            if self.memory_allocations else 0
        addr = highest_end
        self.memory_allocations[addr] = size
        needed = addr + size - len(self.working_memory)
        if needed > 0:
            self.working_memory.extend(b'\x00' * needed)
            self.byte_tags.extend([None] * needed)
        return addr

    def free_memory(self, addr: int) -> bool:
        """Free an allocation, returning its bytes to the shared pool.

        The minimum working memory block [0, 64) cannot be freed.
        """
        if addr not in self.memory_allocations:
            return False
        if addr == 0:
            return False
        size = self.memory_allocations.pop(addr)
        for i in range(addr, min(addr + size, len(self.byte_tags))):
            self.byte_tags[i] = None
        self._forget_absent_packets()
        if self.substrate is not None:
            self.substrate.shared_memory_pool += size
        return True

    def _forget_absent_packets(self):
        """Unspent budget is destroyed when the last tagged byte leaves memory."""
        present = {t for t in self.byte_tags if t is not None}
        for pid in list(self.packet_energy.keys()):
            if pid not in present:
                del self.packet_energy[pid]
                self.packet_drawn.pop(pid, None)
                self.packet_metadata.pop(pid, None)

    def compute_upkeep(self) -> float:
        if self.state == "SUSPENDED":
            return 0.0
        mem_size = self.get_working_memory_size()
        total = BASE_UPKEEP + mem_size / MEMORY_COST_DIVISOR
        if self.state == "DORMANT":
            total *= DORMANT_UPKEEP_FRACTION
        return total


class Substrate:
    """The runtime environment (v3 parameters)."""

    def __init__(self, seed: int = 42, phase_mode: str = 'long',
                 packet_e_rich: float = PACKET_E_RICH,
                 packet_e_lean: float = PACKET_E_LEAN,
                 packet_rate: int = PACKET_RATE,
                 buffer_depth: int = BUFFER_DEPTH,
                 population_cap: int = POPULATION_CAP,
                 initial_buffer_packets: int = 0,
                 offspring_maturation_delay: int = 0):
        self.seed = seed
        self.rng = random.Random(seed)
        self.organisms: dict[int, Organism] = {}
        self.next_organism_id = 0
        self.tick = 0
        self.data_stream = PacketBuffer(
            seed, phase_mode, packet_e_rich, packet_e_lean,
            packet_rate=packet_rate, buffer_depth=buffer_depth,
            initial_buffer_packets=initial_buffer_packets)
        self.initial_shared_memory_pool = SHARED_MEMORY_POOL
        self.shared_memory_pool = SHARED_MEMORY_POOL
        # Corpse pool is a list, not a dict keyed by address: many organisms
        # share address 0, and a dict silently loses their memory.
        self.corpse_pool: list[tuple[int, int]] = []   # (size, tick_of_death)
        self.population_cap = max(1, int(population_cap))
        self.offspring_maturation_delay = max(
            0, int(offspring_maturation_delay))
        self.ancestry: list[dict] = []
        self.birth_log: list[dict] = []
        self.births = 0
        self.deaths = 0
        self.memory_allocation_failures_total = 0
        # Ecological capture instrumentation. Only valid, full-packet READs
        # enter the denominator; malformed READs are tracked separately.
        self.capture_attempts_tick = 0
        self.capture_successes_tick = 0
        self.capture_attempts_total = 0
        self.capture_successes_total = 0
        self.invalid_read_attempts_total = 0
        self.capture_history: list[dict] = []
        self.read_event_log: list[dict] = []
        self.transform_event_log: list[dict] = []
        self.divide_event_log: list[dict] = []
        self.cap_replacement_log: list[dict] = []

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def corpse_allocated_bytes(self) -> int:
        return sum(size for size, _death_tick in self.corpse_pool)

    def expire_corpse_memory(self) -> int:
        """Return expired corpse blocks exactly once; return bytes reclaimed."""
        still_warm = []
        reclaimed = 0
        for size, death_tick in self.corpse_pool:
            if self.tick - death_tick >= CORPSE_POOL_TTL:
                self.shared_memory_pool += size
                reclaimed += size
            else:
                still_warm.append((size, death_tick))
        self.corpse_pool = still_warm
        return reclaimed

    def add_organism(self, genome: list[tuple], reserve: float = None,
                     parent_id: int = -1, generation: int = 0,
                     lineage_label: str | None = None,
                     founder_lineage_id: int | None = None) -> Organism | None:
        if reserve is None:
            reserve = INITIAL_EXECUTION_RESERVE
        if self.shared_memory_pool < MIN_WORKING_MEMORY:
            return None
        self.shared_memory_pool -= MIN_WORKING_MEMORY
        if founder_lineage_id is None and parent_id == -1:
            founder_lineage_id = self.next_organism_id
        org = Organism(genome, self.next_organism_id, reserve,
                       parent_id, generation, substrate=self,
                       lineage_label=lineage_label,
                       founder_lineage_id=founder_lineage_id)
        self.next_organism_id += 1
        self.organisms[org.id] = org
        self.births += 1
        self.birth_log.append({
            "id": org.id, "parent": parent_id, "generation": generation,
            "birth_tick": self.tick, "birth_reserve": reserve,
            "lineage_label": lineage_label,
            "founder_lineage_id": founder_lineage_id,
        })
        return org

    def remove_organism(self, org_id: int, cause: str = ""):
        """Mark dead and release memory to the corpse pool exactly once."""
        org = self.organisms.get(org_id)
        if not org:
            return
        if org.state == "DEAD":
            return
        org.state = "DEAD"
        org.death_cause = cause
        reached_first_extraction = (
            org.first_positive_extraction_tick is not None)
        if not reached_first_extraction:
            self._classify_causing_offspring_displacements(
                org.id, "died_before_first_extraction", self.tick)
        for _addr, size in org.memory_allocations.items():
            self.corpse_pool.append((size, self.tick))
        org.memory_allocations.clear()
        org.packet_energy.clear()
        org.packet_drawn.clear()
        org.packet_metadata.clear()
        self.deaths += 1
        self.ancestry.append({
            "id": org.id, "parent": org.parent_id,
            "generation": org.generation, "genome_length": org.genome_length,
            "birth_tick": org.birth_tick, "death_tick": self.tick,
            "cause": cause, "divides": org.total_divides,
            "divide_attempts": org.divide_attempts,
            "first_divide_tick": org.first_divide_tick,
            "last_valid_read_tick": org.last_valid_read_tick,
            "first_positive_extraction_tick": org.first_positive_extraction_tick,
            "reached_first_positive_extraction": reached_first_extraction,
            "terminal_reserve": org.execution_reserve,
            "death_stage": (
                "post_first_offspring_instantiation"
                if org.first_divide_tick is not None
                else "post_extraction_pre_first_offspring"
                if org.first_positive_extraction_tick is not None
                else "pre_first_extraction"),
            "read_stage_at_death": (
                "post_first_valid_read"
                if org.last_valid_read_tick is not None
                else "pre_first_valid_read"),
            "lineage_label": org.lineage_label,
            "founder_lineage_id": org.founder_lineage_id,
            "last_transform_op": org.last_transform_op,
            "last_transform_extent": org.last_transform_extent,
            "last_transform_tick": org.last_transform_tick,
            "transform_execution_counts":
                dict(org.transform_execution_counts),
        })

    def refresh_terminal_reserve(self, org: Organism) -> None:
        """Synchronize death telemetry after post-instruction cost charging."""
        for record in reversed(self.ancestry):
            if record["id"] == org.id:
                record["terminal_reserve"] = org.execution_reserve
                return

    def _classify_causing_offspring_displacements(
            self, offspring_id: int, outcome: str, tick: int) -> None:
        """Resolve displacement outcomes without changing ecological state."""
        for event in self.cap_replacement_log:
            if (event["causing_offspring_id"] == offspring_id and
                    event["causing_offspring_outcome"] == "unresolved"):
                event["causing_offspring_outcome"] = outcome
                event["causing_offspring_outcome_tick"] = tick

    def displacement_viability_summary(self) -> dict:
        """Attribute cap events to the first-extraction fate of each birth."""
        outcomes = {
            "unresolved": 0,
            "reached_first_extraction": 0,
            "died_before_first_extraction": 0,
        }
        for event in self.cap_replacement_log:
            outcomes[event["causing_offspring_outcome"]] += 1
        live_events = [event for event in self.cap_replacement_log
                       if event["victim_was_live"]]
        doomed_live = sum(
            event["causing_offspring_outcome"] ==
            "died_before_first_extraction"
            for event in live_events)
        unresolved_live = sum(
            event["causing_offspring_outcome"] == "unresolved"
            for event in live_events)
        return {
            "all_cap_events": len(self.cap_replacement_log),
            "live_displacements": len(live_events),
            "live_displacements_caused_by_offspring_dying_before_first_extraction":
                doomed_live,
            "doomed_offspring_fraction_of_live_displacements": (
                doomed_live / len(live_events) if live_events else None),
            "unresolved_causing_offspring_live_displacements": unresolved_live,
            "unresolved_causing_offspring_all_cap_events":
                outcomes["unresolved"],
            "outcomes": outcomes,
        }

    # ------------------------------------------------------------------
    # Environment interaction
    # ------------------------------------------------------------------

    def read_packet(self, org: Organism, addr: int, length: int) -> bool:
        """Read a whole packet into working memory. Returns True on success.

        READ is all-or-nothing: the organism must have room to receive the
        packet. A partial read is a failure, not a partial success.
        """
        if length < PACKET_SIZE or not org.is_memory_range_valid(addr, PACKET_SIZE):
            self.invalid_read_attempts_total += 1
            org.fail_flag = True
            return False
        self.capture_attempts_tick += 1
        self.capture_attempts_total += 1
        previous_read_tick = org.last_valid_read_tick
        read_event = {
            "tick": self.tick,
            "organism_id": org.id,
            "lineage_label": org.lineage_label,
            "founder_lineage_id": org.founder_lineage_id,
            "birth_tick": org.birth_tick,
            "age": self.tick - org.birth_tick,
            "is_first_valid_read": previous_read_tick is None,
            "previous_valid_read_tick": previous_read_tick,
            "read_interval": (
                None if previous_read_tick is None
                else self.tick - previous_read_tick),
            "capture_success": False,
        }
        org.last_valid_read_tick = self.tick
        packet = self.data_stream.read()
        if packet is None:
            self.read_event_log.append(read_event)
            org.fail_flag = True
            return False
        self.capture_successes_tick += 1
        self.capture_successes_total += 1
        for i, b in enumerate(packet.data):
            org.working_memory[addr + i] = b
            org.byte_tags[addr + i] = packet.packet_id
        org.packet_energy[packet.packet_id] = packet.e_budget
        org.packet_drawn[packet.packet_id] = 0.0
        org.packet_metadata[packet.packet_id] = (packet.max_reducible, len(packet.data))
        read_event["capture_success"] = True
        self.read_event_log.append(read_event)
        org.fail_flag = False
        return True

    def apply_transform(self, org: Organism, op: int,
                        addr: int, length: int) -> tuple[int, float]:
        """Apply a transform. Returns (byte_reduction, replenishment).

        Extraction rules (report 1b):
          - reduction grants energy only if can_reconstruct() is True
          - the draw is bounded by the packet's remaining budget
          - expansion charges the organism, capped by what was previously
            drawn from that packet, and credits the budget back
          - on expansion the original data is left intact in memory
        """
        if not org.is_memory_range_valid(addr, length):
            org.fail_flag = True
            return (0, 0.0)

        original = bytes(org.working_memory[addr:addr + length])
        transformed = compute_transform(op, original)
        notional_size = len(transformed)
        lossless = can_reconstruct(op, original, transformed)

        # Tagged bytes in the region, grouped by packet
        packets_in_region: dict[int, int] = {}
        for i in range(addr, addr + length):
            tag = org.byte_tags[i] if i < len(org.byte_tags) else None
            if tag is not None:
                packets_in_region[tag] = packets_in_region.get(tag, 0) + 1

        replenishment = 0.0
        charge_total = 0.0

        for pid, n_before in packets_in_region.items():
            if pid not in org.packet_energy:
                continue
            max_red, _s = org.packet_metadata.get(pid, (max(1, length), length))
            max_red = max(1, max_red)
            share = n_before / length if length else 0.0
            # Bytes of this packet removed (positive) or added (negative)
            effective_red = (length - notional_size) * share
            budget_total = org.packet_energy[pid] + org.packet_drawn.get(pid, 0.0)
            delta = (budget_total / max_red) * effective_red

            if delta > 0:
                if not lossless:
                    continue  # footprint may shrink, but no energy is granted
                available = org.packet_energy.get(pid, 0.0)
                actual = min(delta, available)
                org.packet_energy[pid] = available - actual
                org.packet_drawn[pid] = org.packet_drawn.get(pid, 0.0) + actual
                replenishment += actual
            elif delta < 0:
                # Expansion: charge is capped by what was drawn from this packet.
                # On a fresh packet nothing was drawn, so the charge is zero and
                # the instruction is merely wasted.
                drawn = org.packet_drawn.get(pid, 0.0)
                charge = min(abs(delta), drawn)
                if charge > 0:
                    org.execution_reserve -= charge
                    org.packet_energy[pid] = org.packet_energy.get(pid, 0.0) + charge
                    org.packet_drawn[pid] = drawn - charge
                    charge_total += charge

        # ------------------------------------------------------------------
        # Write behaviour
        # ------------------------------------------------------------------
        if notional_size < length:
            for i in range(notional_size):
                org.working_memory[addr + i] = transformed[i]
            # Reclaim memory only when the transformed region is exactly the
            # allocation rooted at addr. A partial-extent transform changes
            # bytes inside an allocation; it does not release the untouched
            # suffix of that allocation back to the shared pool.
            alloc_size = org.memory_allocations.get(addr)
            if alloc_size is not None and length == alloc_size:
                freed = alloc_size - notional_size
                org.memory_allocations[addr] = notional_size
                if freed > 0:
                    self.shared_memory_pool += freed
            for i in range(addr + notional_size, addr + length):
                if i < len(org.byte_tags):
                    org.byte_tags[i] = None
            org._forget_absent_packets()
            byte_reduction = length - notional_size
        elif notional_size == length:
            for i in range(length):
                org.working_memory[addr + i] = transformed[i]
            byte_reduction = 0
        else:
            # Expansion: leave the original data intact so a subsequent
            # transform can still process the original packet.
            byte_reduction = 0

        org.execution_reserve += replenishment
        if replenishment > 0 and org.first_positive_extraction_tick is None:
            org.first_positive_extraction_tick = self.tick
            self._classify_causing_offspring_displacements(
                org.id, "reached_first_extraction", self.tick)
        org.fail_flag = False
        # R3 = byte reduction (0 on expansion), R4 = replenishment x10
        org.registers[3] = int(byte_reduction)
        org.registers[4] = int(replenishment * 10)
        self.transform_event_log.append({
            "tick": self.tick,
            "organism_id": org.id,
            "lineage_label": org.lineage_label,
            "founder_lineage_id": org.founder_lineage_id,
            "opcode": op,
            "extent": length,
            "byte_reduction": byte_reduction,
            "replenishment": replenishment,
            "r4": org.registers[4],
        })
        return (byte_reduction, replenishment)

    # ------------------------------------------------------------------
    # Reproduction
    # ------------------------------------------------------------------

    def transfer_fraction(self, org: Organism) -> float:
        """tau = R5/256, with a fallback to 128/256 when R5 is out of range."""
        r5 = org.registers[5]
        if not isinstance(r5, int) or r5 <= 0 or r5 >= 256:
            r5 = 128
        return r5 / 256.0

    def reproduce(self, org: Organism) -> int | None:
        """Attempt reproduction via DIVIDE. Returns offspring ID or None.

        No clamp and no viability threshold: the parent transfers whatever tau
        specifies. If memory permits, the offspring is instantiated with that
        reserve and viability emerges from its subsequent ledger. A return of
        None denotes materialisation failure, not a classified offspring death.
        """
        org.last_reproduction_failure_reason = None
        if not org.gestation_buffer:
            org.fail_flag = True
            org.last_reproduction_failure_reason = "missing_gestation_buffer"
            return None
        if org.execution_reserve <= 0:
            org.fail_flag = True
            org.last_reproduction_failure_reason = "parent_reserve_exhausted"
            return None

        offspring_genome = self._mutate_genome(org.gestation_buffer)
        if not offspring_genome:
            org.fail_flag = True
            org.last_reproduction_failure_reason = "empty_offspring_genome"
            return None

        org.gestation_buffer = []
        # The copied genome has been materialised into offspring_genome, so
        # the parent's gestation allocation is no longer needed. Return it on
        # every completed DIVIDE attempt, including materialisation failure.
        if org.gestation_region is not None:
            org.free_memory(org.gestation_region)
        org.gestation_region = None
        org.gestation_size = 0
        org.copy_pointer = 0

        if self.shared_memory_pool < MIN_WORKING_MEMORY:
            org.fail_flag = True
            org.last_reproduction_failure_reason = "insufficient_shared_memory"
            self.memory_allocation_failures_total += 1
            return None

        # Memory feasibility precedes reserve commitment. ALLOC/COPY work and
        # the discarded gestation buffer remain sunk costs, but no reserve is
        # transferred or destroyed when no offspring can exist to receive it.
        tau = self.transfer_fraction(org)
        transfer_reserve = org.execution_reserve * tau
        org.execution_reserve -= transfer_reserve

        # Instantiation is now guaranteed. Record it before victim sampling so
        # a self-displaced parent retains correct lifetime telemetry.
        org.divides_this_cycle += 1
        org.total_divides += 1
        if org.first_divide_tick is None:
            org.first_divide_tick = self.tick

        # Population cap: sample uniformly over every resident, including the
        # reproducing parent. Reproduction grants no displacement immunity.
        # remove_organism() is the single release point; the reaper in
        # Simulation.step() does not release again.
        causing_offspring_id = self.next_organism_id
        while len(self.organisms) >= self.population_cap:
            victim_id = self.rng.choice(list(self.organisms.keys()))
            victim = self.organisms[victim_id]
            victim_next_opcode = (
                victim.genome[victim.pc][0]
                if 0 <= victim.pc < len(victim.genome) else None)
            self.cap_replacement_log.append({
                "tick": self.tick,
                "parent_id": org.id,
                "parent_lineage_label": org.lineage_label,
                "causing_offspring_id": causing_offspring_id,
                "causing_offspring_outcome": "unresolved",
                "causing_offspring_outcome_tick": None,
                "victim_id": victim_id,
                "victim_is_reproducing_parent": victim_id == org.id,
                "victim_was_live": victim.state != "DEAD",
                "victim_lineage_label": victim.lineage_label,
                "victim_founder_lineage_id": victim.founder_lineage_id,
                "victim_transform_op": victim.last_transform_op,
                "victim_transform_extent": victim.last_transform_extent,
                "victim_pc": victim.pc,
                "victim_next_opcode": victim_next_opcode,
                "victim_last_execution_tick": victim.last_execution_tick,
                "victim_pending_divide": (
                    victim.state != "DEAD" and
                    victim.last_execution_tick != self.tick and
                    victim_next_opcode == DIVIDE),
            })
            self.remove_organism(victim_id, "displacement")
            del self.organisms[victim_id]

        self.shared_memory_pool -= MIN_WORKING_MEMORY
        offspring = Organism(
            genome=offspring_genome,
            organism_id=self.next_organism_id,
            execution_reserve=transfer_reserve,
            parent_id=org.id,
            generation=org.generation + 1,
            substrate=self,
            lineage_label=org.lineage_label,
            founder_lineage_id=org.founder_lineage_id,
        )
        offspring.maturation_remaining = self.offspring_maturation_delay
        self.next_organism_id += 1
        self.organisms[offspring.id] = offspring
        self.births += 1
        self.birth_log.append({
            "id": offspring.id, "parent": org.id,
            "generation": offspring.generation,
            "birth_tick": self.tick,
            "birth_reserve": transfer_reserve,
            "maturation_delay": self.offspring_maturation_delay,
            "lineage_label": offspring.lineage_label,
            "founder_lineage_id": offspring.founder_lineage_id,
        })

        org.fail_flag = False
        return offspring.id

    def _mutate_genome(self, genome: list[tuple]) -> list[tuple]:
        """Indels at DIVIDE. Substitutions are applied per instruction copied,
        inside COPY_UNIT / COPY_BLOCK."""
        new_genome = list(genome)
        if self.rng.random() < MUTATION_INSERTION:
            pos = self.rng.randint(0, len(new_genome))
            op = self.rng.randint(0, MAX_OPCODE)
            args = tuple(self.rng.randint(0, 255) for _ in range(2))
            new_genome.insert(pos, (op,) + args)
        if self.rng.random() < MUTATION_DELETION and len(new_genome) > 1:
            pos = self.rng.randint(0, len(new_genome) - 1)
            new_genome.pop(pos)
        if self.rng.random() < MUTATION_DUPLICATION and len(new_genome) > 0:
            pos = self.rng.randint(0, len(new_genome) - 1)
            new_genome.insert(pos + 1, new_genome[pos])
        return new_genome