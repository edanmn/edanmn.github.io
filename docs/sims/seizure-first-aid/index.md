# Seizure First Aid Simulator

A student has a seizure and you have to work the problem in real time: keep them safe, time it,
and decide whether this one needs an ambulance. Seven scenarios, picked at random, and they do
not all end the same way.

<iframe src="main.html" width="100%" height="900" class="microsim" title="Seizure First Aid Simulator" loading="lazy"></iframe>

[Open the simulator full screen](main.html){ .md-button }

## How to use it
1. Press start. You get the situation first: where you are, and whether the student has a
   seizure action plan.
2. Watch the figure and the clock. The seizure moves through stiffening, convulsing, and then
   the groggy period afterwards when they are not yet awake.
3. Click the actions you would actually take. Some are right, some are wrong, and one of them
   is only right once the jerking stops.
4. Decide about 911 yourself. The simulator will not prompt you.
5. When it ends you get a report: what you did, when you did it, what you missed, and what to
   write down afterwards.

## What it teaches
- Timing is the decision. Five minutes of convulsing makes a seizure an emergency, and nobody
  can judge five minutes by feel.
- Most seizures do not need an ambulance. Three of the seven scenarios do not, and calling
  anyway costs a family money without helping the student.
- Four things make it an emergency regardless of the clock: a first seizure, water, injury, or
  a second seizure before the person recovers.
- The recovery position comes after the jerking eases, not during.
- Restraining someone, putting anything in their mouth, or giving water are all wrong, and the
  simulator will tell you why if you try them.
- Rescue medicine is only ever given when that student's own plan says so.
- The last step is documentation. What you write down is what the neurologist uses.

!!! warning
    This is a learning tool, not medical advice or certification. For free training in
    Minnesota, see the [Epilepsy Foundation of Minnesota](https://www.epilepsyfoundationmn.org/get-support/seizure-smart-trainings/).
    A student's care is set by their healthcare provider and their seizure action plan.

## About this simulator
- Built as a single HTML file with inline SVG, so it works offline and on a phone.
- Learning objective: apply seizure first aid under time pressure and judge when 911 is needed.
- Source chapter: [Seizure First Aid](../../chapters/02-seizure-first-aid/index.md)
