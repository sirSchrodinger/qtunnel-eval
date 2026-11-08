# Video script (narration is generated with Piper TTS, voice en_US-lessac-medium)

## Slide 1

Can frontier language models do exact quantum tunnelling physics without a computer? I am a physics undergraduate, and this is my entry for the micro1 Eval Hackathon. I built thirteen closed book tasks in nanoelectronics, graded every answer by code against exact references, and tested four Claude models plus a small open model. Spoiler: I set out to find a limitation, and for the frontier models I did not find one. This video shows what I built, why you can trust the numbers, and what I did learn.

## Slide 2

Why does this matter? In tunnel oxides, resonant tunnelling diodes, scanning tunnelling microscopes and molecular junctions, small errors in the physics become big errors in the current. A three tenths of an electron volt error in a barrier height changes a tunnelling current by about a factor of two, and every two tenths of a nanometre of oxide costs about a decade of current. Engineers normally use a transfer matrix program. The question is whether a model can be trusted as a quick first pass calculator, giving the exact number, not an approximation.

## Slide 3

Here is one task. An electron crosses an aluminium gallium arsenide barrier between gallium arsenide contacts, with different effective masses, and the model must use the right boundary conditions and report the exact transmission. The reference is zero point zero five eight zero one. The naive boundary condition gives zero point zero four seven five five, eighteen percent off, so it fails. The grader reads only the last answer line, compares it with a three percent tolerance, and grades the outcome, not the method. If an answer misses, it is compared with what common wrong methods give, so every failure is labelled. Sixty six unit tests check the grader, including deliberately wrong answers. And every reference is recomputed with a second solver, using explicit wave amplitudes and an analytic resonance condition.

## Slide 4

The results. At default reasoning effort, Sonnet, Opus and Fable got all thirty nine trials right. Haiku missed one. The small three billion parameter open model got two out of thirty nine. At low reasoning effort the Claude models scored thirty seven, thirty nine, thirty eight and thirty eight out of thirty nine. So there is a clear spread between a small model and the frontier models, but almost no headroom among the frontier models. I tested tools off, thirteen tasks, three trials each, and I do not claim a ranking among the Claude models.

## Slide 5

What did the failures look like? Haiku once put the effective mass in the denominator of the decay constant, so a heavier electron tunnelled more, which is the wrong direction. At low reasoning effort there were four misses, and in three of them the model replaced the exact calculation I asked for by a named approximation. Opus used a Lorentzian estimate for the resonance width. Haiku used the Herring formula for the splitting. Each one said in a caveat that this was only an estimate, and each one still put a single number on the answer line. The small open model fails differently: it breaks the answer format, assumes full transmission on resonance for an asymmetric structure, or just writes wrong numbers.

## Slide 6

There is one more finding, and it is about me. In my first run, all four models failed the resonance energy task, in twelve out of twelve trials. Eleven of those trials gave the same answer, zero point zero eight six two electron volts, and my reference said zero point zero eight one eight. The guide says a zero percent pass rate everywhere is a warning sign, so I checked my reference with an independent analytic resonance condition. The models were right and I was wrong: my helper function had given the contacts the free electron mass. I fixed it, re-graded the stored outputs without any new model calls, and kept the first pass grades in the files.

## Slide 7

My takeaway. Closed book, textbook level quantum mechanics is no longer where these frontier models fail. One Haiku trial used about thirty seven thousand hidden reasoning tokens to sum Airy function series by hand and still got the answer right. The remaining risk is commitment to exactness: when pushed, a model may swap in an approximation, mention it in a caveat, and still hand you one number. A grader that only reads the number cannot see that, so eval authors should score declared approximations separately. And a bug in the reference is now more likely than a mistake by the model, so build a second solver.

## Slide 8

To reproduce it, install the requirements, run the grader tests, run the independent check of the references, and run the harness with your own API key. Raw outputs and transcripts of every trial are in the zip. Two honest notes. First, the API backends of my harness were not tested against a live API, the results come from the Claude Code command line backend. Second, Claude drafted the tasks, the code and this write up on my instruction, and I have not yet reviewed every task myself. The README says so, and explains how I checked the work instead. Thank you for watching.
