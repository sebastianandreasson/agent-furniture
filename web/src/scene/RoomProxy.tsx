import { Grid } from '@react-three/drei'

export function RoomProxy({ showGrid }: { showGrid: boolean }) {
  return (
    <group name="room-proxy">
      <mesh position={[0, -12, 0]} receiveShadow>
        <boxGeometry args={[6200, 20, 6200]} />
        <meshStandardMaterial color="#151a20" roughness={0.96} metalness={0} />
      </mesh>
      <mesh position={[0, 1400, -3000]} receiveShadow>
        <boxGeometry args={[6200, 2800, 24]} />
        <meshStandardMaterial
          color="#242a31"
          roughness={1}
          transparent
          opacity={0.46}
        />
      </mesh>
      <mesh position={[-3000, 1400, 0]} receiveShadow>
        <boxGeometry args={[24, 2800, 6200]} />
        <meshStandardMaterial
          color="#242a31"
          roughness={1}
          transparent
          opacity={0.38}
        />
      </mesh>
      {showGrid && (
        <Grid
          position={[0, 1, 0]}
          args={[6000, 6000]}
          cellSize={100}
          cellThickness={0.65}
          cellColor="#46515d"
          sectionSize={1000}
          sectionThickness={1.3}
          sectionColor="#8d9cad"
          fadeDistance={6500}
          fadeStrength={1}
          infiniteGrid={false}
        />
      )}
    </group>
  )
}
