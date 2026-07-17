import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type {
  CameraView,
  Placement,
  TransformMode,
  Vector3Tuple,
} from '../types'

export const DEFAULT_PLACEMENT: Placement = {
  positionMm: [0, 0, 0],
  rotationDeg: [0, 0, 0],
}

type LayerKey = 'splat' | 'furniture' | 'room' | 'grid'

type EditorState = {
  activeDesignId: string | null
  placements: Record<string, Placement>
  transformMode: TransformMode
  snapping: boolean
  showHelpers: boolean
  cameraView: CameraView
  layers: Record<LayerKey, boolean>
  setActiveDesign: (id: string) => void
  setPlacement: (id: string, placement: Placement) => void
  setPosition: (id: string, positionMm: Vector3Tuple) => void
  setRotation: (id: string, rotationDeg: Vector3Tuple) => void
  resetPlacement: (id: string) => void
  setTransformMode: (mode: TransformMode) => void
  setSnapping: (enabled: boolean) => void
  setShowHelpers: (visible: boolean) => void
  setCameraView: (view: CameraView) => void
  toggleLayer: (layer: LayerKey) => void
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set) => ({
      activeDesignId: null,
      placements: {},
      transformMode: 'translate',
      snapping: true,
      showHelpers: true,
      cameraView: 'perspective',
      layers: { splat: true, furniture: true, room: true, grid: true },
      setActiveDesign: (id) => set({ activeDesignId: id }),
      setPlacement: (id, placement) =>
        set((state) => ({
          placements: { ...state.placements, [id]: placement },
        })),
      setPosition: (id, positionMm) =>
        set((state) => ({
          placements: {
            ...state.placements,
            [id]: {
              ...(state.placements[id] ?? DEFAULT_PLACEMENT),
              positionMm,
            },
          },
        })),
      setRotation: (id, rotationDeg) =>
        set((state) => ({
          placements: {
            ...state.placements,
            [id]: {
              ...(state.placements[id] ?? DEFAULT_PLACEMENT),
              rotationDeg,
            },
          },
        })),
      resetPlacement: (id) =>
        set((state) => ({
          placements: {
            ...state.placements,
            [id]: DEFAULT_PLACEMENT,
          },
        })),
      setTransformMode: (transformMode) => set({ transformMode }),
      setSnapping: (snapping) => set({ snapping }),
      setShowHelpers: (showHelpers) => set({ showHelpers }),
      setCameraView: (cameraView) => set({ cameraView }),
      toggleLayer: (layer) =>
        set((state) => ({
          layers: { ...state.layers, [layer]: !state.layers[layer] },
        })),
    }),
    {
      name: 'querycad-editor-v1',
      partialize: ({ placements, activeDesignId, showHelpers }) => ({
        placements,
        activeDesignId,
        showHelpers,
      }),
    },
  ),
)
