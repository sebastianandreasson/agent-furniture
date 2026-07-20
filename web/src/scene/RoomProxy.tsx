import { Grid } from '@react-three/drei'

export function RoomProxy({
  showRoom,
  showGrid,
}: {
  showRoom: boolean
  showGrid: boolean
}) {
  return (
    <group name="room-proxy">
      {showRoom && (
        <>
          <mesh position={[0, -12, 0]} receiveShadow>
            <boxGeometry args={[6200, 20, 6200]} />
            <meshStandardMaterial
              color="#ebe9e3"
              roughness={0.98}
              metalness={0}
            />
          </mesh>
          <mesh position={[0, 1400, -3000]} receiveShadow>
            <boxGeometry args={[6200, 2800, 24]} />
            <meshStandardMaterial color="#fbfaf7" roughness={1} metalness={0} />
          </mesh>
          <mesh position={[-3000, 1400, 0]} receiveShadow>
            <boxGeometry args={[24, 2800, 6200]} />
            <meshStandardMaterial color="#f4f2ec" roughness={1} metalness={0} />
          </mesh>
        </>
      )}
      {showGrid && (
        <Grid
          position={[0, 1, 0]}
          args={[6000, 6000]}
          cellSize={100}
          cellThickness={0.65}
          cellColor="#c7c9c5"
          sectionSize={1000}
          sectionThickness={1.3}
          sectionColor="#969d99"
          fadeDistance={6500}
          fadeStrength={1}
          infiniteGrid={false}
        />
      )}
    </group>
  )
}
