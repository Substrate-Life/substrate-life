# Conservation is not an ecology

*What a digital evolution project taught me about fitness, architecture, and the value of running the smallest complete system*

At one point, every accounting test in Substrate passed. Energy reserves balanced exactly, and every resource packet and block of shared memory could be traced from creation to consumption. Nothing appeared from nowhere and nothing quietly vanished.

The ecology we thought we were testing did not exist.

The population harness had generated a fresh resource packet inside each organism's cycle. Every organism got its own private supply. The bookkeeping was impeccable because each private packet was conserved. But the scientific question depended on organisms competing for one finite stream. Earlier organisms were supposed to consume packets that later organisms might miss. By cloning the supply per organism, the harness had deleted resource competition while preserving all three invariants.

This is a useful kind of failure. It is also an uncomfortable one. Conservation had been the project's strongest safeguard, and it worked exactly as designed. It proved that the implemented system was honest. It could not prove that we had implemented the right system.

Digital evolution is worth the trouble because it lets researchers start with executable organisms, run generations quickly, and preserve records that are difficult or impossible to recover from natural populations. In principle, every resource transfer, mutation, birth, and death can be inspected. That control makes a digital system unusually powerful when its substrate carries the biology of interest, and unusually misleading when it does not.

Tierra established that self-replicating programs can compete for CPU time and memory as ecological resources, and Avida became the platform on which much of modern digital-evolution research is conducted. Substrate belongs to that research tradition without sharing code or an instruction set with either system; it asks the narrower question of what a computational substrate must provide before selection can express a difference at all.

Substrate is a digital evolution project in which organisms execute genomes, transform resources, reproduce, and compete. Its development exposed a strict requirement: selection can act only on differences that the substrate carries through a complete population lifecycle. Conserved resources, extra energy, or an isolated birth do not by themselves show that one lineage will grow faster than another.

The original ambition was to let metabolism, replication, and ecology evolve together instead of assigning organisms a hard-coded fitness score. That ambition survived. Most of the original experimental stories did not.

The five stories that follow share one architectural lesson. The system could obey its rules and account honestly for its resources while its design changed what selection could see. An accurate measurement could still track the wrong part of the lifecycle. Serial copying could suppress extra fecundity. A tight reserve margin could turn a small disadvantage into lethal failure. Surplus income could balance perfectly and still have no route to population growth. One shared wallet could fuse reproduction with survival. Packet cloning later exposed the same gap at the ecological scale: conservation described the system that ran, but could not establish that the system contained the life-history choices or interactions the experiment was meant to study.

These are conditional, cross-platform predictions rather than established results outside Substrate. Tierra, Avida, and other systems can test the claims whose relevant mechanisms they instantiate. One prediction is that, when offspring are copied serially and copy time dominates the reproductive cycle, each additional offspring incurs nearly another full copy delay, reducing or eliminating its growth-rate advantage. A separate prediction is that, where one reserve funds execution, reproduction, persistence, and provisioning, changing offspring number or provisioning will also change viability.

## Fitness is a lifecycle property

The first mistake was treating quantities that were easy to measure as if they were fitness.

Standing reserve looked promising. So did energy income and attempted births. Each says something real about an organism. None, by itself, says how a lineage grows in the population.

That distinction matters because Substrate has overlapping lifetimes and ecological regulation. An offspring can be instantiated and die before it extracts any energy. A parent can survive long enough to produce several offspring in isolation but rarely reach that age in a regulated population. A birth can displace a resident. A vacancy rule can reject reproduction after the parent has already paid for copying. Memory pressure can change which organisms reach the next stage.

For this project, fitness means whether a lineage increases when rare in the regulated population, not how much energy one organism holds or how many births it attempts. Established offspring matter because they survive long enough to enter that population process. Even then, some may contribute more future descendants than others.

This sounds obvious after the fact. It was not obvious while the system was producing clean reserve traces and plausible birth counts. The easier a number is to log, the easier it is to promote it beyond what it measures.

## Replication architecture decides whether fecundity is available

The original organisms copied genomes one instruction at a time. At the shortest viable genome length, eleven instructions, the copy loop took 26 simulation time steps per offspring. Copying dominated the reproductive cycle.

That created a structural constraint. Producing a second offspring required paying nearly the same serial copy delay again. Parameter tuning could make organisms richer, but it could not make extra fecundity competitive while serial copying consumed most of the lifecycle. Under a predefined growth benchmark, one offspring still had an advantage even at the optimistic floor of one time step per copied instruction.

The solution was not another energy adjustment. It was a new instruction, `COPY_BLOCK`, which copied a block in one time step while retaining an energy cost that scaled with length. That changed what evolution could express. Surplus income could now fund additional real copy-and-divide bouts without adding a full serial copy loop each time.

This did not prove that higher fecundity would win in a population. It opened the channel. The distinction is important: implementing a route from surplus to more offspring is mechanism evidence, not selection evidence.

## Reserve margin controls whether selection looks graded or lethal

A second pattern emerged from energy treatments. What mattered was the organism's runway: how much reserve remained compared with the costs it had to pay before its next chance to earn energy. With little runway, a small extra cost became lethal. With more room, a cost could appear as a gradual disadvantage instead.

Separate historical assays using different cost manipulations showed the two regimes. At `E=129`, adding inert instructions pushed the lineage into failure before its next extraction. At `E=300`, a lineage paying for a wasteful extra transform declined gradually from an equal-frequency start. Its decline was still inconclusive at the preregistered checkpoint; only a clearly labeled post-hoc extension made the downward trend pronounced.

The finding is not a universal numerical cutoff. The cost of reaching the next income event depends on the genome, memory state, instruction order, and scheduler. The old interpreter tried to replace that path with a fixed offspring threshold. Removing the shortcut let the lifecycle determine whether a cost was survivable.

## Income has no automatic route to fitness

A richer organism is not necessarily a fitter organism.

In the original one-offspring architecture, two genotypes could earn different amounts and still follow the same reproductive schedule once both cleared the viability boundary. If extra income changed neither timing, survival, establishment, nor later contribution, the surplus had nowhere to go.

The project briefly tried to test the income channel by comparing separate populations at packet energies of 300 and 500. The saved 500-energy run had not actually received its intended input, but the deeper problem was the design itself. More food can support more organisms without giving each organism a lasting income advantage. Population density rises until competition pushes income per organism back toward its costs. Separate monocultures therefore cannot reveal which genotype uses the same shared supply more effectively.

`COPY_BLOCK` fixed the organism-side expressibility problem by letting surplus fund another copied bout. It did not solve the ecological identification problem. A valid efficiency comparison would still need both genotypes in the same population and packet stream, with their lifecycle outcomes tracked separately.

Income matters only through an implemented route to timing, persistence, reproductive work, provisioning, establishment, or later reproduction. Calling income "fitness" skips the mechanism that connects the two.

## One wallet coupled fecundity and viability

The next problem was not a missing channel but too many channels sharing one state variable.

In the earlier design, organisms paid ordinary execution, reproductive work, parental persistence, and offspring provisioning from one reserve. An apparent fecundity change therefore also changed parental runway and offspring quality. Producing more offspring meant spending more on copying and division. Transferring more reserve to offspring left less for the parent. Transferring less created offspring with less time to reach their first extraction.

Removing the static offspring threshold made this visible. Every materially allocatable offspring was instantiated with its actual transfer and then faced the normal scheduler. At a fixed population limit, an under-provisioned offspring could displace a viable resident and then die before feeding. In two mutation-free runs containing only the no-threshold genotype and observed for one 17-step reproductive cycle, 144 of 338 live displacements were already traced to offspring that died before first extraction. The fate of another 108 causing offspring was still unresolved when observation stopped, and one reproducing parent had been selected as a victim.

Those runs were not a competition assay and did not establish an optimum. They showed that the coupling was active enough to alter population turnover.

A constant external hazard could separate physical removal from birth events, but it could not repair the overloaded reserve. An organism could remain physically alive while lacking the energy needed to execute the recovery path. The project did not need another regulator trick. It needed an explicit allocation vocabulary.

The revised design therefore split reserve into somatic and reproductive accounts. Extraction income is allocated between them by a heritable fraction. Basal upkeep and ordinary instruction overhead draw from the somatic side. Reproduction-specific allocation, copying and division work, gestation upkeep, and offspring provisioning draw from the reproductive side. This does not make survival and reproduction independent. High reproductive allocation can still starve soma, and vacancy competition still matters. It does make the direct trade-off explicit and potentially evolvable rather than hiding it inside one wallet.

Two small end-to-end implementations now balance exactly. They verify mechanics only. Mutation was disabled, and allocation contrasts, evolutionary runs, and fitness inference remain untested.

## Control makes evolution easier to interpret and less open

Every time the project tightened an assay, it changed the question.

Fixed genomes are useful for proving that a channel exists. Restricting mutation to one locus can show whether evolution uses that channel within a defined architecture. Freezing schedules and ecology can isolate a causal contrast. None of those experiments answers what an open population will do when metabolism, timing, provisioning, genomic background, and ecological exposure all change together.

The usual instinct is to treat more control as unqualified scientific improvement. Here it creates a real tension. Control improves identification by removing routes evolution might use. The open system restores those routes but makes a background-independent causal effect much harder to identify.

The cleanest response is to separate the claims. A fixed-genome experiment can show that a mechanism changes a lifecycle quantity. A restricted-locus experiment can show that evolution uses it under those constraints. An open experiment can report the distribution of joint genotype, phenotype, and ecological outcomes under a specified mutation process and environment. Evidence at one level should not be promoted to the next.

## Review and execution do different jobs

The split-reserve transaction model went through repeated specification review. The reviews improved it. They fixed the accounting boundaries, clarified which operations had to succeed or fail as a unit, separated measured from inferred quantities, and forced provisional choices into the open.

Then the smallest executable slice found three defects the reviews had missed.

The extraction test used synthetic values rather than values produced by an actual reversible operation. Undoing a transform credited the organism's current account split instead of the account that had originally funded the packet. The ledger also omitted memory and costs incurred by the transform itself.

All three defects lived at the contact point between clean abstractions and running behavior. After they were corrected, the exact reserve, packet, and memory ledgers passed independent executable audit.

The lesson is not that review is useless. Without the reviewed invariants, the failures would have been harder to recognize. The lesson is that review and execution answer different questions. Once the causal intent and accounting rules are coherent, another pass over the prose is a poor substitute for building the smallest complete path.

The population implementation and focused tests also exercised stalls that occurred midway through a cycle, cleanup after failed gestation or reproductive work, and ordinary-cost accounting when memory ran short. These checks exposed and repaired failure-path hazards without requiring an evolutionary run. The packet-cloning error was different: it showed that even perfect failure handling and exact conservation could coexist with the wrong ecology.

## A conserved model can still implement the wrong ecology

The packet-cloning failure deserves its own rule because it would have survived the project's strongest existing checks.

Conservation asks whether resources appear, disappear, or get counted twice inside the implemented boundary. It does not ask whether that boundary has the right shape. A private conserved packet for each organism is perfectly compatible with exact accounting. It is also incompatible with a scientific claim about competition for one shared stream.

The corrected population harness uses a single consumptive buffer with five exogenous packet arrivals per tick. A successful READ removes one packet. When eight organisms are scheduled against five arrivals, the late organisms can miss. In the retained 20-tick trace, organisms captured 91 packets and missed 14 times. All three ledgers still closed.

That gives simulation verification two separate axes.

First, the flows must conserve. Second, the interaction topology must match the intended ecology. Resource arrival must be independent of organism count when the model says it is exogenous. Shared resources must actually be shared. Capture must be exclusive when one organism's use is supposed to deny another. Scheduler order and exposure must be observable rather than assumed away.

A closure proof certifies honest bookkeeping about the system that was built. It cannot certify that the system is relevant to the question being asked.

The mechanics are now verified, but the evolutionary result remains open. The project has not yet shown that allocation strategies evolve, converge on an evolutionarily stable strategy, or respond causally to hazard in an open population. It has also not tested whether host execution produces the resource differences that the digital organisms are supposed to consume. Sound bookkeeping makes those experiments possible; it does not supply their results.

## Build the smallest ecology that can prove you wrong

Digital evolution is often sold on openness: give organisms a substrate, let mutation and selection work, and see what emerges. The hard part is that the substrate decides what can emerge long before selection begins.

If replication is serial, fecundity may be unavailable. If one reserve pays for everything, several life-history traits collapse into one coupling. If surplus has no route to timing or recruitment, it has no fitness meaning. If resources are cloned per organism, there is no competition to select on. Evolution cannot discover a distinction the architecture has erased.

In this project, the productive sequence was to state the accounting and causal claims, expose the unresolved choices, and run the smallest complete slice capable of contradicting them.

The executable slices caught synthetic transform accounting, stale gestation after failed reproduction, and private packet supply hidden behind perfect conservation. Each problem appeared only when the mechanism ran from end to end.

That is enough to justify the next step here, not a universal law. Before asking what evolution does, run the smallest ecology that can show whether there is anything for selection to act on.

The implementation, retained evidence, failed designs, and byte-preserved audit transcripts are available in the public [`substrate-life` repository](https://github.com/Substrate-Life/substrate-life).
