/** A millimetre-scale product-lighting rig for reading furniture joinery and relief. */
export function StudioLighting() {
  return (
    <>
      <ambientLight intensity={0.62} />
      <hemisphereLight args={['#fffdf7', '#c9c3b8', 0.52]} />

      <directionalLight
        name="studio-key"
        castShadow
        color="#fff2df"
        position={[-2600, 3900, 3200]}
        intensity={4.2}
        shadow-mapSize={[2048, 2048]}
        shadow-camera-near={100}
        shadow-camera-far={10000}
        shadow-camera-left={-3400}
        shadow-camera-right={3400}
        shadow-camera-top={3200}
        shadow-camera-bottom={-800}
        shadow-bias={-0.00015}
        shadow-normalBias={1.5}
      />

      <directionalLight
        name="studio-fill"
        color="#dce8f2"
        position={[2600, 1900, 2600]}
        intensity={0.95}
      />
      <directionalLight
        name="studio-rim"
        color="#fff6e9"
        position={[1200, 2800, -2600]}
        intensity={1.15}
      />
    </>
  )
}
