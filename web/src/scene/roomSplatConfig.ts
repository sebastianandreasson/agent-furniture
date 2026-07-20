import roomSplatUrl from '../../public/splats/mipnerf360-room.spz?url'

/**
 * QueryCAD world transform for the real-photo Mip-NeRF 360 room sample.
 * Its reconstruction units have no survey authority; this transform registers
 * it visually with QueryCAD's millimetre furniture workspace.
 */
export const ROOM_SPLAT = Object.freeze({
  assetUrl: roomSplatUrl,
  sourceUrl:
    'https://huggingface.co/kishimisu/3d-gaussian-splatting-webgl/blob/main/room.ply',
  datasetUrl: 'https://jonbarron.info/mipnerf360/',
  rendererUrl: 'https://github.com/sparkjsdev/spark',
  mmPerSourceUnit: 440,
  positionMm: [220, 1200, 690] as const,
  rotationRad: [1.831232, 1.076556, 1.309395] as const,
})
