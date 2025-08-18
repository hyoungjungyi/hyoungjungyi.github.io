import { useState } from 'react';
import MindMap from './MindMap';
import './App.css';

function App() {
  return (
    <div className="flex h-full bg-white">
      {/* 왼쪽 텍스트 영역 */}
      <div className="flex flex-col justify-center items-center w-1/2 p-8">
        <div className="bg-black text-white rounded-[50px] p-8 text-center">
          <h1 className="text-4xl font-bold">HALEY YI</h1>
          <p className="mt-4 text-lg">Undergrad AI Researcher</p>
          <p className="mt-4 text-lg">@ Korea University Business School</p>
          <p className="mt-4 text-lg">software entrepreneurship program</p>
        </div>
      </div>

      {/* 오른쪽 MindMap 영역 */}
      <div className="flex justify-center items-center w-full md:w-1/2 p-10">
        <div className="w-full h-full" style={{ boxSizing: 'border-box' }}>
          <MindMap />
        </div>
      </div>

    </div>
  );
}

export default App;
