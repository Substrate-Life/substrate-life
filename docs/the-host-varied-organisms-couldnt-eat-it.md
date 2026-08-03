# The host varied. The organisms couldn't eat it.

*What a failed host-coupling experiment says about compression-based metabolism*

Substrate began with a fairly literal ambition: digital organisms should live on real computational resources. The host machine would supply an environment. Organisms would extract energy by finding structure in what the machine emitted. Useful information would become food without a designer assigning a fitness score.

The host did vary. Under CPU load, scheduler latency changed strongly, reproducibly, and in two directions at once. Typical wake-ups became faster while the upper tail became worse.

The organisms still could not eat it.

The failure was not a lack of environmental variation. It was a mismatch between the structure the host produced and the structure the metabolism could consume. Substrate's two transforms detect repetition. The host mostly produced shifting distributions. Every apparent case of positive compression came from repeated bytes introduced by serialization, not from the host process itself.

That is a more useful result than "host coupling did not work." It identifies a constraint that applies before evolution begins.

## The metabolism chose the environment in advance

Substrate organisms receive byte packets and can apply one of two transforms. RLE compresses runs of identical bytes. DIFF+RLE first replaces bytes with adjacent differences, then compresses repeated differences. When a transformed packet is smaller than its input, the freed bytes fund replenishment, subject to explicit caps and costs.

This looked neutral when the system was designed. The substrate measured byte reduction rather than assigning value to particular content. Organisms could choose which transform to run.

But the transform table had already decided which kinds of information could become nutritional. RLE can eat repeated values. DIFF+RLE can eat repeated changes. A signal with a changing mean, variance, or tail can carry real information while offering neither kind of run.

The system did not have a general compression metabolism. It had a repetition metabolism.

That distinction stayed hidden while experiments used synthetic packets built to alternate between RLE-friendly and DIFF-friendly phases. Those environments contained exactly the patterns the transforms recognized. The organisms appeared to sense and exploit environmental structure because the environment and metabolism had been designed around each other.

A real host was under no obligation to speak that language.

## The first positive result was padding

The first host probe sampled aggregate CPU and operating-system counters at 10 millisecond intervals. Counter deltas were serialized into fixed-width fields and grouped into packets. RLE won every packet in both a short exploratory trace and a registered one-hour trace. The result looked almost absurdly strong.

It was also artificial.

Most counter changes were small integers stored in wide fields. Their high-order bytes were zero. The serializer had wrapped each real value in repeated padding, and RLE compressed the padding. The host supplied small counter changes; the encoding supplied the byte runs.

Three alternative encodings of the retained hour removed or changed that padding. The apparent richness disappeared. Under the unpadded projections, almost every packet expanded under both transforms. A transform could still "win," but winning usually meant expanding less than the other transform. It did not mean extracting energy.

This exposed an important reporting error. Transform rankings sound ecological: RLE regime, DIFF regime, switching, drift. None of those categories matters to a compression-funded metabolism unless some packets actually compress. Positive reduction is the first gate.

The counter result did not show that the host lacked structure. It showed that fixed-width serialization could manufacture the one kind of structure the metabolism knew how to eat.

## The host really did respond

Scheduler wake latency offered a cleaner signal. It was directly experienced by the recorder, retained at nanosecond resolution, and did not require identity-bearing process events. Two compile workers could saturate the host's two cores while the recorder measured lateness against absolute deadlines.

I predicted that CPU contention would increase p99 wake lateness by at least tenfold. A sixty-second pilot falsified that prediction. The increase was about 3.9-fold.

The shape was stranger than a simple slowdown. Median lateness fell under load, from about 111 microseconds to 81 microseconds, while p99 rose from roughly 0.48 to 1.87 milliseconds. Busy cores plausibly avoided some idle-state exit cost while contention worsened rare wakes, although CPU power-state residency was not measured. The mechanism remains an inference. The opposing distributional movement does not.

A registered fifteen-minute sham/compile characterization reproduced the shape. Under compile load, the median, p90, and p95 were all lower. P99 was about 2.5 times higher.

The host was not static. Load changed its latency distribution, and a scalar notion of "more load means more latency" was already too crude.

The remaining question was whether the direct packet mapping preserved enough of that response for the transforms to see it.

## My second explanation also failed

Before the characterization, I predicted that packet morphology would remain flat. That part was right. My explanation was wrong.

I expected the response to live in such rare tail events that most packets would never contain one. Ten consecutive latency values went into each primary packet. If only one sample in a hundred shifted, perhaps nine packets in ten would look unchanged, and one unusual value inside the tenth would barely perturb its bytes. Aggregation would wash out the response.

The occupancy result killed that account. Using the pilot's idle p99 as a fixed threshold, 30.2 percent of compile packets contained at least one exceedance. Tail events reached plenty of packets. Every thirty-second slice contained them.

Morphology stayed flat anyway.

Across 9,000 packets per arm, DIFF beat RLE on most packets in both conditions. The winner counts were almost identical. There was no five-minute switching and no registered block drift.

More importantly, neither transform positively compressed a single packet. RLE: zero of 9,000 in each arm. DIFF: zero of 9,000 in each arm.

"DIFF won" meant only that DIFF expanded an incompressible packet slightly less.

The actual mechanism is simpler than aggregation. Consecutive nanosecond latency values differ, and their adjacent byte differences differ. RLE finds no repeated bytes. DIFF+RLE finds no repeated deltas. Moving the median or stretching the tail changes which incompressible numbers appear. It does not create repetition where none existed.

The host signal reached the packets. The transforms had no way to metabolize it.

## Why quantization would answer a different question

Once the result is visible, the obvious rescue is to quantize latency. Replace nanosecond values with a few buckets, or encode the maximum, p95, and p99 of a window. Load would change those features. Bucketing would also create repeated symbols, giving RLE something to compress.

That would probably work. It would also change the claim.

The original question was whether organisms could exploit structure emitted by the host through a direct mapping. A quantizer designed after learning where the signal lives would manufacture the runs the metabolism requires. The nutritious environment would be the quantizer's output. The designer would have selected the feature, resolution, thresholds, and timescale that made the known contrast visible.

Engineered sensors are legitimate systems. They are not evidence that this metabolism found host structure on its own. Substrate exists to supply mechanisms rather than strategies, so the host line stops here rather than rescuing itself with a better feature extractor.

## A predictive metabolism would ask the right successor question

The result reflects back on the metabolism. Information becomes nutritional only when an organism has a mechanism capable of exploiting it. A fixed table of RLE and DIFF opcodes lets organisms choose between two designer-supplied strategies. It does not let them construct a model of whatever structure the environment happens to offer.

Prediction provides a more general architecture. A probabilistic predictor assigns a probability to the next value given its history. Better predictions imply shorter ideal code lengths. A genome that specified a heritable, mutable predictor could exploit changes in marginal distributions or temporal dependence without the substrate deciding in advance that runs were the relevant pattern.

The energy rule cannot reward raw accuracy. A constant stream is perfectly predictable, so raw accuracy would make it maximally nutritious for everyone. Energy has to come from predictive advantage over a fixed reference model: the organism's code length compared with the reference code length on the same next value using the same available history.

That reference is where the designer re-enters. A weak baseline makes ordinary regularity nutritious. A strong baseline can consume all available structure before organisms receive any advantage. The reference predictor, gain divisor, replenishment cap, representation, scoring rule, model costs, and learning state all define the fitness landscape. They would need the same scrutiny that Substrate's extraction and replenishment rules eventually received.

Predictive advantage would also have to allocate a bounded external resource budget rather than create energy from a score. Predictor memory, execution, and learning would carry explicit costs. The gain is architectural, not magical: within those constraints, the organism chooses a heritable model instead of selecting from a fixed list of nutritious patterns.

That is a successor project, not a post-hoc repair.

## The cheap test

The founding host-coupling question now has an answer with a mechanism attached.

The host varied. Its response to load was measurable, reproducible, and non-monotonic. The repetition metabolism could not consume the distributional currency in which that variation appeared. Fixed-width counters seemed nutritious only because their serializer inserted repeated zeros. Direct latency was incompressible from the start.

Both predictions that mattered were stated before their runs, and both were falsified in useful ways. The p99 effect was about 3.9-fold rather than at least tenfold. Tail events reached 30 percent of compile packets rather than being averaged away. Each failure removed a convenient explanation and exposed the next mechanism.

Anyone attempting host coupling with a compression-based metabolism can check this cheaply. Record the direct candidate stream. Apply the live transforms. Count positive reductions before exposing a single organism. If one transform wins only by expanding less, there is no nutritional channel to evolve against.

That test cannot prove that every host signal is incompressible or that predictive metabolism will evolve. It can prevent a long organism experiment from being built around structure the metabolism cannot consume.

The implementation, registrations, raw captures, failed designs, and complete reduction are retained in the public [`substrate-life` repository](https://github.com/Substrate-Life/substrate-life).
