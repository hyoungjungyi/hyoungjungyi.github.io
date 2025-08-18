export const graphData = {
  nodes: [
    { id: "root", color: "black" },

    { id: "RESEARCHER", group: "root" , alwaysShow : true},
    { id: "BUILDER", group: "root", alwaysShow : true },
    { id: "HACKER", group: "root", alwaysShow : true },

    // researcher subnodes
    { id: "Paper1", group: "RESEARCHER", 
      description: "AI 논문 1: 대규모 언어모델 연구", 
      link: "https://arxiv.org/abs/xxxx" },
    { id: "Paper2", group: "RESEARCHER", 
      description: "AI 논문 2: 의료영상 분석", 
      link: "https://arxiv.org/abs/yyyy" },

    // builder subnodes
    { id: "App1", group: "BUILDER", 
      description: "React + Flask 기반 웹앱", 
      link: "https://github.com/..." },
    { id: "App2", group: "BUILDER", 
      description: "모바일 헬스케어 앱", 
      link: "https://github.com/..." },

    // hacker subnodes
    { id: "Hackathon1", group: "HACKER", 
      description: "삼성 해커톤 1위, 의료 AI 솔루션", 
      link: "https://devpost.com/..." },
    { id: "Hackathon2", group: "HACKER", 
      description: "USC 해커톤 대상, VR 협업툴", 
      link: "https://devpost.com/..." }
  ],
  links: [
    { source: "root", target: "RESEARCHER" , color: "red" },
    { source: "root", target: "BUILDER", color: "green" },
    { source: "root", target: "HACKER", color: "blue" },

    { source: "RESEARCHER", target: "Paper1" },
    { source: "RESEARCHER", target: "Paper2" },
    { source: "BUILDER", target: "App1" },
    { source: "BUILDER", target: "App2" },
    { source: "HACKER", target: "Hackathon1" },
    { source: "HACKER", target: "Hackathon2" }
  ]
};
