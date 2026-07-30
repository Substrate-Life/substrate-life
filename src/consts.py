# Substrate — v3 Parameter Set
# Instruction set, constants, and core types.
# Authoritative specification: project-report.md sections 1a-1d.

# Instruction opcodes
NOP = 0
JUMP = 1
JUMPZ = 2
JUMPNZ = 3
MOV = 4
ADD = 5
SUB = 6
AND = 7
OR = 8
XOR = 9
CMP = 10
READ = 11
WRITE = 12
ALLOC = 13
FREE = 14
TRANSFORM = 15
SLEEP = 16
DIE = 17
ALLOC_OFFSPRING = 18
COPY_UNIT = 19
DIVIDE = 20
SET_P = 21
READ_GESTATION = 22
COPY_BLOCK = 23

MAX_OPCODE = COPY_BLOCK  # inclusive upper bound for mutation

OPCODE_NAMES = {
    NOP: "NOP", JUMP: "JUMP", JUMPZ: "JUMPZ", JUMPNZ: "JUMPNZ",
    MOV: "MOV", ADD: "ADD", SUB: "SUB", AND: "AND", OR: "OR",
    XOR: "XOR", CMP: "CMP", READ: "READ", WRITE: "WRITE",
    ALLOC: "ALLOC", FREE: "FREE", TRANSFORM: "TRANSFORM",
    SLEEP: "SLEEP", DIE: "DIE",
    ALLOC_OFFSPRING: "ALLOC_OFFSPRING", COPY_UNIT: "COPY_UNIT",
    DIVIDE: "DIVIDE", SET_P: "SET_P", READ_GESTATION: "READ_GESTATION",
    COPY_BLOCK: "COPY_BLOCK",
}

# Base costs. Size-dependent extras are added by the engine:
#   ALLOC            1 + size/64
#   ALLOC_OFFSPRING  5 + size/64
#   TRANSFORM        3 + len/64
#   COPY_BLOCK       2 + n/64
INSTRUCTION_COST = {
    NOP: 1, JUMP: 1, JUMPZ: 1, JUMPNZ: 1, MOV: 1,
    ADD: 2, SUB: 2, AND: 2, OR: 2, XOR: 2, CMP: 2,
    READ: 10, WRITE: 2,
    ALLOC: 1, FREE: 1, SLEEP: 1, DIE: 1,
    ALLOC_OFFSPRING: 5, COPY_UNIT: 2, DIVIDE: 5,
    SET_P: 1, READ_GESTATION: 2,
    TRANSFORM: 3,
    COPY_BLOCK: 2,
}

# v3 parameters
BASE_UPKEEP = 0.1
MEMORY_COST_DIVISOR = 640
PERSISTENT_COST_DIVISOR = 640
DORMANT_UPKEEP_FRACTION = 0.1
MIN_WORKING_MEMORY = 64
INITIAL_EXECUTION_RESERVE = 100
POPULATION_CAP = 500
PACKET_SIZE = 256
BUFFER_DEPTH = 8
PACKET_RATE = 5  # constant packets per tick, independent of population
CORPSE_POOL_TTL = 5
MUTATION_SUBSTITUTION = 0.001  # per instruction copied
MUTATION_INSERTION = 0.01      # per genome per DIVIDE
MUTATION_DELETION = 0.01       # per genome per DIVIDE
MUTATION_DUPLICATION = 0.001   # per genome per DIVIDE
SHARED_MEMORY_POOL = 80 * 1024  # 80 KB
PACKET_E_RICH = 300  # extractable energy per rich packet
PACKET_E_LEAN = 300  # same budget, different structure

# Default transfer fraction register value: tau = R5 / 256
DEFAULT_TRANSFER_R5 = 128

# Transform opcodes
TRANSFORM_RLE = 0
TRANSFORM_DIFF = 1
TRANSFORM_ENCODE_BASE = 2
TRANSFORM_FILTER_LOW = 3
TRANSFORM_HASH_SUM = 4