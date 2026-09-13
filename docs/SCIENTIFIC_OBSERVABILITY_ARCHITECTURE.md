# Scientific observability architecture

`ScientificObservationService` reads scientific frame pages from the sealed `SCIENTIFIC_TRACE` CAS artifact. Dispatcher memory is a live accelerator only; terminal playback reconstructs from CAS. The observation API is read-only and remains separate from `LiveSandboxService`.
