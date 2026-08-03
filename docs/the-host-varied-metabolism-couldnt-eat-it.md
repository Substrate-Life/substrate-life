# The host varied. The metabolism couldn't eat it.

*What a failed host-coupling experiment says about compression-based metabolism*

Substrate began with a fairly literal ambition: digital organisms should live on real computational resources. The host machine would supply an environment. Organisms would extract energy by finding structure in what the machine emitted. Useful information would become food without a designer assigning a fitness score.

The broader risk is architectural: a digital-evolution system can expose organisms to a changing world while preselecting which changes count as resources. If the metabolism and environment speak different statistical languages, evolution has nothing to work with.

The host did vary. During the compile arm, scheduler latency changed strongly and in two directions at once. Typical wake-ups became faster while the upper tail became worse. The metabolism still could not eat it.

No organism received these host-derived packets. The pre-assay mapping gate failed: the live transforms could not extract positive reduction from them.

The failure was not a lack of environmental variation. It was a mismatch between the structure the host produced and the structure the metabolism could consume. Substrate's two transforms detect repetition. The host mostly produced shifting distributions. The only strong, sustained positive compression in the tested host traces came from repeated zero bytes introduced by fixed-width serialization, not from host temporal structure.

That is a more useful result than "host coupling did not work." It identifies a constraint that applies before evolution begins.

## The metabolism chose the environment in advance

Substrate organisms receive byte packets and can apply one of two transforms. RLE compresses runs of identical bytes. DIFF+RLE first replaces bytes with adjacent differences, then compresses repeated differences. When a transformed packet is smaller than its input, the freed bytes fund replenishment, subject to explicit caps and costs.

This looked neutral when the system was designed. The substrate measured byte reduction rather than assigning value to particular content. Organisms could choose which transform to run.

But the transform table had already decided which kinds of information could become nutritional. RLE can eat repeated values. DIFF+RLE can eat repeated changes. A signal with a changing mean, variance, or tail can carry real information while offering neither kind of run.

The system did not have a general compression metabolism. It had a repetition metabolism.

That distinction stayed hidden while experiments used synthetic packets built to alternate between RLE-friendly and DIFF-friendly phases. Those environments contained exactly the patterns the transforms recognized. The organisms appeared to sense and exploit environmental structure because the environment and metabolism had been designed around each other.

A real host was under no obligation to speak that language.

## The first positive result was padding

The first host probe sampled aggregate CPU and operating-system counters. Counter deltas were serialized into fixed-width fields and grouped into packets. RLE won every packet in both a short exploratory trace and a registered one-hour trace. The result looked almost absurdly strong, but most counter changes were small integers stored in wide fields. Their high-order bytes were zero. The serializer had wrapped each real value in repeated padding, and RLE compressed the padding. The host supplied small counter changes; the encoding supplied the byte runs.

Three alternative encodings of the retained hour removed or changed that padding. Under the normalized projection, almost every packet expanded under both transforms. ULEB128 and the low-byte projection supplied no sustained positive-compression regime; their median RLE reduction was zero. A transform could still "win," but winning usually meant expanding less than the other transform. It did not mean extracting energy.

This exposed an important reporting error. Transform rankings sound ecological: RLE regime, DIFF regime, switching, drift. None of those categories matters to a compression-funded metabolism unless some packets actually compress. Positive reduction is the first gate.

The counter result did not show that the host lacked structure. It showed that fixed-width serialization could manufacture the one kind of structure the metabolism knew how to eat.

## The host really did respond

Scheduler wake latency offered a cleaner signal. It was directly experienced by the recorder, retained at nanosecond resolution, and did not require identity-bearing process events. Two continuous compile workers ran on a host with two logical CPUs while the recorder measured lateness against absolute deadlines.

I predicted that the compile period's p99 wake lateness would be at least ten times the idle pilot value. The pilot falsified that prediction. The increase was about 3.9-fold.

The shape was stranger than a simple slowdown. Typical lateness fell during compilation while the upper tail grew. Busy cores plausibly avoided some idle-state exit cost while contention worsened rare wakes, although CPU power-state residency was not measured. The mechanism remains an inference. The opposing distributional movement does not.

A registered sham/compile characterization reproduced the shape. During the compile arm, the median, p90, and p95 were all lower, while p99 was about 2.5 times higher. Because the arms ran sequentially in fixed order, this characterizes two host periods under specified conditions; it does not by itself isolate compilation causally or establish cross-time generality.

The two periods differed, and a scalar notion of "more load means more latency" was too crude. The remaining question was whether the direct packet mapping preserved enough of that difference for the transforms to see it.

## My second explanation also failed

Before the characterization, I predicted that packet morphology would remain flat. That part was right. My explanation was wrong.

I expected the response to live in such rare tail events that most packets would never contain one. Ten consecutive latency values went into each primary packet, so I expected packetization to hide the changed tail from the transforms.

The occupancy result killed that account. Using the pilot's idle p99 as a fixed threshold, 30.2 percent of compile packets contained at least one exceedance. Tail events reached plenty of packets, yet morphology stayed flat.

DIFF beat RLE on most packets in both periods. The winner counts were almost identical, with no five-minute switching or registered block drift. More importantly, neither transform positively compressed a single one of the 9,000 packets in either arm.

"DIFF won" meant only that DIFF expanded an incompressible packet slightly less.

The actual mechanism is simpler than aggregation. Nanosecond latency values rarely repeat, and repeated adjacent byte differences were too scarce to overcome transform overhead. Moving the median or stretching the tail changed which largely incompressible values appeared without creating enough runs for positive reduction.

The host signal reached the packets. The metabolism had no way to consume it.

## Why quantization would answer a different question

Once the result is visible, the obvious rescue is to quantize latency. Replace nanosecond values with a few buckets, or encode the maximum, p95, and p99 of a window. Load would change those features. Bucketing would also create repeated symbols, giving RLE something to compress.

That might work, but it would change the claim. The original question was whether organisms could exploit structure emitted by the host through a direct mapping. A quantizer designed after learning where the signal lives would manufacture the runs the metabolism requires. The nutritious environment would be the quantizer's output. The designer would have selected the feature, resolution, thresholds, and timescale that made the known contrast visible.

Engineered sensors are legitimate systems. They are not evidence that this metabolism found host structure on its own. Substrate exists to supply mechanisms rather than strategies, so the host line stops here rather than rescuing itself with a better feature extractor.

## A predictive metabolism would ask the right successor question

The result reflects back on the metabolism. Information becomes nutritional only when an organism has a mechanism capable of exploiting it. A fixed table of RLE and DIFF opcodes lets organisms choose between two designer-supplied strategies. It does not let them construct a model of whatever structure the environment happens to offer.

Prediction provides a more general architecture. A probabilistic predictor assigns a probability to the next value given its history. Better predictions imply shorter ideal code lengths. A heritable, mutable predictor could make marginal or temporal structure nutritional if it achieved out-of-sample code-length advantage over a fixed, causally online reference predictor.

The energy rule cannot reward raw accuracy. Raw predictability would wrongly credit trivial structure: a constant stream can be predicted perfectly, but a competent reference should predict it too and leave little or no gain. Energy has to come from predictive advantage over a fixed reference model: the organism and reference must assign probabilities to the same next value, in the same discrete representation, from the same causally available history, under a proper coding or scoring rule.

That reference is where the designer re-enters. A weak baseline makes ordinary regularity nutritious. A strong baseline can consume all available structure before organisms receive any advantage. The reference predictor, gain divisor, replenishment cap, representation, scoring rule, model costs, and learning state all define the fitness landscape. They would need the same scrutiny that Substrate's extraction and replenishment rules eventually received.

Predictive advantage would also have to allocate a bounded external resource budget rather than create energy from a score. Predictor memory, execution, and learning would carry explicit costs. The gain is architectural, not magical: within those constraints, the organism chooses a heritable model instead of selecting from a fixed list of nutritious patterns. This is a successor project rather than a post-hoc repair.

## The cheap test

The founding host-coupling question now has an answer with a mechanism attached.

The host periods differed measurably and non-monotonically. The repetition metabolism could not consume the distributional currency in which that variation appeared. Fixed-width counters seemed nutritious only because their serializer inserted repeated zeros. Direct latency was incompressible from the start.

Both predictions that mattered were stated before their runs, and both were falsified in useful ways. The p99 effect was about 3.9-fold rather than at least tenfold. Tail events reached 30 percent of compile packets rather than being too sparse to reach most packets. Flat morphology had been predicted correctly; the sparse-tail explanation for it had not. Each failure removed a convenient explanation and exposed the next mechanism.

Anyone attempting host coupling with a compression-based metabolism can check this cheaply. Record the direct candidate stream. Apply the live transforms. Count positive reductions before exposing a single organism. If one transform wins only by expanding less, there is no nutritional channel to evolve against.

That test cannot prove that every host signal is incompressible or that predictive metabolism will evolve. It can prevent a long organism experiment from being built around structure the metabolism cannot consume.

The implementation, registrations, raw captures, failed designs, and complete reduction are retained in the public [`substrate-life` repository](https://github.com/Substrate-Life/substrate-life).
