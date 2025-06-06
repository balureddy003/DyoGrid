export interface Agent { input_key: string; type: string; name: string; system_message: string; description: string; icon: string; index_name: string; }

import h1 from '@/assets/h1.png';
import lBrain from '@/assets/l-brain.png';
import lPen from '@/assets/l-pen.png';
import lSearch from '@/assets/l-search.png';
import lAi from '@/assets/l-ai.png';
import lSensor from '@/assets/l-sensor.png';
import lAnalyzer from '@/assets/l-analyzer.png';
import lRag from '@/assets/l-rag.png';
  // Helper functions to get avatar source and fallback
export const getAvatarSrc = (user: string) => {
    switch (user.toLowerCase()) {
      case 'user':
        return h1;
      case 'magenticoneorchestrator':
        return lBrain;
      case 'coder':
        return lPen;
      case 'filesurfer':
        return lSearch;
      case 'websurfer':
        return lSearch;
      case 'ragagent':
        return lSearch;
      case 'executor':
        return lPen;
      case 'taskresult':
        return lAi;
      case 'sensorsentinel':
        return lSensor;
      case 'compliancesentinel':
        return lSensor;
      case 'trendanalyzer':
        return lAnalyzer;
      case 'transactiontrendanalyzer':
        return lAnalyzer;
      case 'oilgasknowledge':
        return lRag;
      case 'KBAgent'.toLowerCase():
          return lRag;
      case 'MaintanceKBAgent'.toLowerCase():
          return lRag;
      case 'CreditOpportunityRecommender'.toLocaleLowerCase():
          return lAnalyzer;
      default:
        if (user.toLowerCase().includes('rag')) {
          return lRag;
        }
        if (user.toLowerCase().includes('analyzer')) {
          return lAnalyzer;
        }
        if (user.toLowerCase().includes('monitor')) {
          return lSensor;
        }
        return 'https://example.com/default.png';
    }
  };
export  const getAvatarFallback = (user: string) => {
    switch (user.toLowerCase()) {
      case 'user':
        return 'U';
      case 'magenticoneorchestrator':
        return 'O';
      case 'coder':
        return 'C';
      case 'filesurfer':
        return 'F';
      case 'websurfer':
        return 'W';
      case 'ragagent':
        return 'R';
      case 'executor':
        return 'E';
      case 'ai':
        return 'AI';
      default:
        return 'D';
    }
  };

// Comment out or remove the old exports (agentsTeam1, agentsTeam2, etc.)
// export const agentsTeam1 = [...];
// export const agentsTeam2 = [...];
// ...etc...
