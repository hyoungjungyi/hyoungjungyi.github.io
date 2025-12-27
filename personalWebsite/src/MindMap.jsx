import React, { useEffect, useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as d3 from "d3-force-3d";
import { Text } from "@react-three/drei"; 
import ForceGraph3D from "react-force-graph-3d";
import { graphData } from "./assets/graphData";
import * as THREE from 'three';




// Force simulation (d3)
function useForceGraph(data) {
  const [nodes, setNodes] = useState(data.nodes.map((d) => ({ ...d })));
  const [links, setLinks] = useState(data.links.map((d) => ({ ...d })));

  useEffect(() => {
    const simulation = d3.forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d) => d.id).distance(80))
      .force("charge", d3.forceManyBody().strength(-150))
      .force("center", d3.forceCenter(0, 0, 0))
      .force("z", d3.forceZ().strength(0.1))
      .on("tick", () => {
        setNodes([...nodes]);
        setLinks([...links]);
      });

    return () => simulation.stop();
  }, []);

  return { nodes, links };
}

// Node 컴포넌트
function Node({ node }) {
  const ref = useRef();
  useFrame(() => {
    if (ref.current) {
      ref.current.position.set(node.x, node.y, node.z || 0);
    }
  });

  return (
    <group ref={ref}>
      {/* 구 (노드 본체) */}
      <mesh>
        <sphereGeometry args={[5, 16, 16]} />
        <meshStandardMaterial color={node.color || "white"} />
      </mesh>

      {/* 라벨 */}
      <Text
        position={[0, 10, 0]}
        fontSize={4}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {node.id}
      </Text>
    </group>
  );
}

function generateTextCanvas(text) {
  const canvas = document.createElement("canvas");
  canvas.width =2048;   
  canvas.height = 1024;  
  const ctx = canvas.getContext("2d");
  ctx.font = "200px Arial";
  ctx.fillStyle = "black";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText(text, canvas.width / 2, canvas.height / 2);
  return canvas;
}

// Link 컴포넌트
function Link({ link }) {
  const ref = useRef();
  useFrame(() => {
    if (ref.current && link.source && link.target) {
      const start = [link.source.x, link.source.y, link.source.z || 0];
      const end = [link.target.x, link.target.y, link.target.z || 0];
      const mid = start.map((s, i) => (s + end[i]) / 2);

      ref.current.position.set(...mid);

      // 벡터 길이 계산
      const dx = end[0] - start[0];
      const dy = end[1] - start[1];
      const dz = end[2] - start[2];
      const length = Math.sqrt(dx * dx + dy * dy + dz * dz);

      ref.current.scale.set(1, 1, length);

      // 방향 회전
      ref.current.lookAt(...end);
    }
  });

  return (
    <mesh ref={ref}>
      <cylinderGeometry args={[0.5, 0.5, 1]} />
      <meshStandardMaterial color="gray" />
    </mesh>
  );
}

// 전체 그래프
function ForceGraph({ data }) {
  const { nodes, links } = useForceGraph(data);

  return (
    <>
      {links.map((link, i) => (
        <Link key={i} link={link} />
      ))}
      {nodes.map((node, i) => (
        <Node key={i} node={node} />
      ))}
    </>
  );
}

// 최종 Scene
export default function MindMap() {
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <>
      <ForceGraph3D
        graphData={graphData}
        linkWidth={link => 1}
        linkColor={link => link.color || "gray"}
        nodeAutoColorBy="group"
        nodeLabel="id"
        nodeThreeObject={node => {
          if (node.alwaysShow) {
            const sprite = new THREE.Sprite(
              new THREE.SpriteMaterial({
                map: new THREE.CanvasTexture(generateTextCanvas(node.id)),
                depthWrite: false
              })
            );
            sprite.scale.set(200,100 , 1); // 텍스트 크기 조절
            return sprite;
          }
          return undefined; // hover는 nodeLabel로 처리
        }}
        onNodeClick={(node) => {
          // 모든 노드 클릭 시 팝업 표시
          setSelectedNode(node);
        }}
        backgroundColor="#cacacaff"
      />

      {selectedNode && (
        <div
          className="modal-overlay"
          onClick={() => setSelectedNode(null)}
        >
          <div
            className="modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-header">
              <h2>{selectedNode.id}</h2>
              <button
                className="modal-close"
                aria-label="닫기"
                onClick={() => setSelectedNode(null)}
              >
                ×
              </button>
            </div>
            <p>
              {selectedNode.description || "아직 설명이 없어요. 곧 업데이트될 예정입니다."}
            </p>
            {selectedNode.link && (
              <a
                className="modal-link"
                href={selectedNode.link}
                target="_blank"
                rel="noreferrer"
              >
                자세히 보기
              </a>
            )}
          </div>
        </div>
      )}
    </>
  );
}
