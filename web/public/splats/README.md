# Included room splat

`mipnerf360-room.spz` is a browser-compressed copy of the real-photo Mip-NeRF
360 `room` reconstruction published by Kishimisu. The original Mip-NeRF 360
scene was reconstructed from photographs rather than generated imagery. It is
stored locally so the Studio loads deterministically without depending on
cross-origin response headers at runtime.

- Upstream PLY: [Kishimisu room.ply][asset]
- Dataset: [Mip-NeRF 360][dataset]
- Upstream PLY SHA-256: `8df08ddaec8cbdbaecd838990102e758931cb8180dedb53e0686e869f804069c`
- Local SPZ SHA-256: `9b465048b844c6e1bd974fca7e0008b73cc7018e0ac0edae5a9893d0a06f64bd`
- Conversion: `splat-transform v3.1.4`, SPZ version 3, 1,087,406 Gaussians
- Renderer: [Spark][spark], MIT licensed
- Scene use: sample visual context only; not survey or collision geometry

[asset]: https://huggingface.co/kishimisu/3d-gaussian-splatting-webgl/blob/main/room.ply
[dataset]: https://jonbarron.info/mipnerf360/
[spark]: https://github.com/sparkjsdev/spark
