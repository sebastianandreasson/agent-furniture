import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Texture } from 'three'
import { describe, expect, it } from 'vitest'
import {
  addBoxProjectionUvs,
  copyFurnitureScene,
  usesDarkWoodTexture,
} from './furnitureAppearance'

describe('furniture appearance', () => {
  it('selects the built-in bookshelf family instead of a specific design id', () => {
    expect(usesDarkWoodTexture({ model: 'built_in_bookshelf' })).toBe(true)
    expect(usesDarkWoodTexture({ model: 'entryway_bench' })).toBe(false)
  })

  it('adds finite UV coordinates to CadQuery geometry', () => {
    const geometry = new BoxGeometry(1200, 160, 24)
    addBoxProjectionUvs(geometry)
    const uv = geometry.getAttribute('uv')

    expect(uv.count).toBe(geometry.getAttribute('position').count)
    expect(Array.from(uv.array).every(Number.isFinite)).toBe(true)
  })

  it('textures wood while preserving untextured knob materials', () => {
    const source = new Group()
    const wood = new Mesh(
      new BoxGeometry(800, 160, 24),
      new MeshStandardMaterial({ color: '#4b2412' }),
    )
    wood.name = 'shelf'
    const knob = new Mesh(
      new BoxGeometry(20, 20, 20),
      new MeshStandardMaterial({ color: '#986428' }),
    )
    knob.name = 'knob_right'
    source.add(wood, knob)

    const textures = {
      color: new Texture(),
      normal: new Texture(),
      roughness: new Texture(),
    }
    const copy = copyFurnitureScene(source, textures)
    const copiedWood = copy.scene.getObjectByName('shelf') as Mesh
    const copiedKnob = copy.scene.getObjectByName('knob_right') as Mesh
    const woodMaterial = copiedWood.material as MeshStandardMaterial
    const knobMaterial = copiedKnob.material as MeshStandardMaterial

    expect(copiedWood.geometry).not.toBe(wood.geometry)
    expect(woodMaterial).not.toBe(wood.material)
    expect(woodMaterial.map).toBe(textures.color)
    expect(woodMaterial.normalMap).toBe(textures.normal)
    expect(woodMaterial.roughnessMap).toBe(textures.roughness)
    expect(knobMaterial.map).toBeNull()
    expect(knobMaterial.color.getHex()).toBe(
      (knob.material as MeshStandardMaterial).color.getHex(),
    )

    copy.dispose()
  })

  it('isolates material instances so individual part meshes can be highlighted', () => {
    const source = new Group()
    const sharedMaterial = new MeshStandardMaterial({ color: '#4b2412' })
    const selected = new Mesh(new BoxGeometry(30, 200, 2400), sharedMaterial)
    const unselected = new Mesh(new BoxGeometry(1034, 400, 28), sharedMaterial)
    selected.name = 'core_upright_left_left'
    unselected.name = 'counter_left'
    source.add(selected, unselected)

    const copy = copyFurnitureScene(source)
    const copiedSelected = copy.scene.getObjectByName(
      'core_upright_left_left',
    ) as Mesh
    const copiedUnselected = copy.scene.getObjectByName('counter_left') as Mesh

    expect(copiedSelected.material).not.toBe(copiedUnselected.material)

    copy.dispose()
  })
})
