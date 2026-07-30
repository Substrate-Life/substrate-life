"""Data stream with per-packet energy budgets (v3)."""

import random
import hashlib
from consts import PACKET_SIZE, PACKET_RATE, BUFFER_DEPTH, PACKET_E_RICH, PACKET_E_LEAN


class Packet:
    """A data packet with embedded extractable energy."""
    
    def __init__(self, data: bytes, packet_id: int, e_budget: float,
                 max_reducible: int, is_lean: bool = False):
        self.data = data
        self.packet_id = packet_id
        self.e_budget = e_budget  # remaining extractable energy
        self.e_initial = e_budget
        self.max_reducible = max_reducible  # S - S_min
        self.is_lean = is_lean


class DataStream:
    """Generates packets with known structure and energy budgets."""

    def __init__(self, seed: int = 42, phase_mode: str = 'long',
                 packet_e_rich: float = PACKET_E_RICH,
                 packet_e_lean: float = PACKET_E_LEAN):
        self.seed = seed
        self.rng = random.Random(seed)
        self.lcg_state = seed
        self.phase_key = (seed * 7 + 13) % 256
        self.next_packet_id = 0
        self.phase_mode = phase_mode
        # Live, inspectable treatment values. Experiments must report these
        # attributes rather than merely echoing intended constructor inputs.
        self.packet_e_rich = packet_e_rich
        self.packet_e_lean = packet_e_lean

    def _lcg(self) -> int:
        self.lcg_state = (self.lcg_state * 1103515245 + 12345) & 0x7FFFFFFF
        return self.lcg_state

    def _rich_packet(self, tick: int) -> Packet:
        """Runs of exactly 3 identical bytes with varying deltas.
        RLE compresses well (256→172, extraction 131 > 98).
        DIFF expands (256→341, extraction 0 < 98 — capped by drawn=0).
        Specialists are non-viable in opposite phases; switcher survives both.
        """
        data = bytearray(PACKET_SIZE)
        i = 0
        run_val = (tick * 13 + 7) % 256
        while i + 3 <= PACKET_SIZE:
            for j in range(3):
                data[i + j] = run_val
            delta = ((tick * 17 + i * 53) % 100) - 50
            if delta == 0:
                delta = 1
            run_val = (run_val + delta) % 256
            i += 3
        # Fill any remaining bytes
        while i < PACKET_SIZE:
            data[i] = run_val
            i += 1
        s_min = 64
        max_reducible = PACKET_SIZE - s_min
        return Packet(bytes(data), self.next_packet_id,
                      self.packet_e_rich, max_reducible)

    def _lean_packet(self, tick: int) -> Packet:
            """Structure where RLE fails but DIFF succeeds.
            Sawtooth wave: each byte differs from previous, so RLE expands.
            Differences follow a repeating pattern, so DIFF+RLE compresses well.
            Same budget as rich packet (E=300), different structure.
            """
            data = bytearray(PACKET_SIZE)
            for i in range(PACKET_SIZE):
                # Sawtooth: each byte is (i * 7 + tick) % 256
                val = (i * 7 + tick) % 256
                data[i] = val
            # RLE on this data: each byte is different from neighbours → expands
            # DIFF on this data: differences follow pattern (7, 7, 7, ...) → highly compressible
            # Minimum size under DIFF+RLE: first byte + RLE of ~21 diffs (7 repeated 255/7 ≈ 36 times)
            # Actually each diff is 7, so RLE on diffs gives (36, 7) * 7 + first byte = 15 bytes
            s_min = 15
            max_reducible = PACKET_SIZE - s_min
            return Packet(bytes(data), self.next_packet_id,
                          self.packet_e_lean, max_reducible, is_lean=True)

    def generate_packet(self, tick: int) -> Packet:
        """Generate a packet for the current tick based on phase_mode."""
        pid = self.next_packet_id
        self.next_packet_id += 1
        if self.phase_mode == 'monotonic_rich':
            return self._rich_packet(tick)
        elif self.phase_mode == 'monotonic_lean':
            return self._lean_packet(tick)
        elif self.phase_mode == 'short':
            # Alternate every 50 ticks
            period = 50
            phase_tick = (tick // period) % 2
            if phase_tick == 0:
                return self._rich_packet(tick)
            else:
                return self._lean_packet(tick)
        else:  # 'long' (default): 1000 + 200-200 alternation
            if tick < 1000:
                return self._rich_packet(tick)
            elif tick < 2000:
                return self._lean_packet(tick)
            else:
                phase_tick = (tick - 2000) % 400
                if phase_tick < 200:
                    return self._rich_packet(tick)
                else:
                    return self._lean_packet(tick)


class PacketBuffer:
    """Sliding window buffer with constant-rate packet arrival."""

    def __init__(self, seed: int = 42, phase_mode: str = 'long',
                 packet_e_rich: float = PACKET_E_RICH,
                 packet_e_lean: float = PACKET_E_LEAN,
                 packet_rate: int = PACKET_RATE,
                 buffer_depth: int = BUFFER_DEPTH,
                 initial_buffer_packets: int = 0):
        self.stream = DataStream(seed, phase_mode,
                                 packet_e_rich, packet_e_lean)
        self.buffer: list[Packet] = []
        self.max_depth = max(1, int(buffer_depth))
        self.packet_rate = max(1, int(packet_rate))
        self.arrival_counter = 0
        self.current_tick = 0
        self.initial_buffer_packets = max(
            0, min(int(initial_buffer_packets), self.max_depth))
        for _ in range(self.initial_buffer_packets):
            self.buffer.append(self.stream.generate_packet(self.current_tick))

    def advance_tick(self):
        """Advance one tick. May enqueue packets at PACKET_RATE per tick."""
        self.current_tick += 1
        for _ in range(self.packet_rate):
            if len(self.buffer) < self.max_depth:
                self.buffer.append(self.stream.generate_packet(self.current_tick))
            else:
                # Buffer full: discard oldest
                self.buffer.pop(0)
                self.buffer.append(self.stream.generate_packet(self.current_tick))

    def read(self) -> Packet | None:
        """Read and consume the oldest packet. Returns None if buffer empty."""
        if not self.buffer:
            return None
        return self.buffer.pop(0)