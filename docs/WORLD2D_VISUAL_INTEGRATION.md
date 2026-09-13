# World2D visual integration

From a Scenario/World node the user opens a World2D panel. It uses the real backend (`WorldDefinition`, `WorldInstance`, seed, Preview); it never implements a second simulator in the frontend.

## Multi-view world inspection

Three synchronized views, always unequivocally labelled:

- **World Truth** — privileged ground truth;
- **Agent View** — what the agent observes (with its observation mask);
- **Observer View** — the Observer's private truth.

World Truth is never shown as if it were the agent's observation. The views render topology, objects, positions, state, obstacles, resources, and events; ground truth is shown only when authorized.

## World timeline

The timeline integrates step, action, events, state changes, and Observer events. The user can scrub, step forward/backward (visual trace playback, clearly differentiated from runtime rewind), and jump to an event. Playback of a recorded trace is labelled as such; it never pretends to rewind a live runtime.

## Sandbox control

Only the **engineering sandbox** is controllable: Start, Step, Pause, Resume, Stop. It is always labelled `ENGINEERING_SANDBOX · NOT EVIDENCE`. There is no scientific-execution button anywhere in the workspace.

## Separation of state

Simulation state and visual state are kept separate. The render loop is efficient (canvas, requestAnimationFrame); visual state (current step, play/pause, viewport) never alters the recorded world trace.
