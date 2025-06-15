import { useState } from 'react'
import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from '@/components/mode-toggle'
import { LoginCard } from "@/components/login";
import { Button } from "@/components/ui/button"
import ag from '@/assets/ag.png';
import axios from 'axios'
import { Footer } from '@/components/Footer'
import { Agent, Team, useTeamsContext } from '@/contexts/TeamsContext';

const BASE_URL = import.meta.env.VITE_BASE_URL || "local";
const ALLWAYS_LOGGED_IN =
  import.meta.env.VITE_ALLWAYS_LOGGED_IN === "true" ? true : false;
const ACTIVATION_CODE = import.meta.env.VITE_ACTIVATON_CODE || "0000";

export default function Bench() {
  const { teams } = useTeamsContext();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team>(teams[0]);
  const [isAuthenticated, setIsAuthenticated] = useState(BASE_URL)
  const [output, setOutput] = useState<string>('');
  const [running, setRunning] = useState(false);

  const handleLogin = (email: string, password: string) => {
    if (password === ACTIVATION_CODE || ALLWAYS_LOGGED_IN) {
      setIsAuthenticated(true)
    }
  }
  const handleTeamSelect = (team: Team) => {
    setAgents(team.agents);
    setSelectedTeam(team);
  }

  const runBench = async () => {
    try {
      setRunning(true);
      await axios.post(`${BASE_URL}/bench/run_team`, {
        team_id: selectedTeam.team_id,
        scenario: "scenarios/basic.jsonl",
        config: "OAI_CONFIG_LIST.json",
        repeats: 1
      });
      const res = await axios.get(`${BASE_URL}/bench/team/${selectedTeam.team_id}`);
      if (Array.isArray(res.data) && res.data.length > 0) {
        setOutput(res.data[0].csv);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setRunning(false);
    }
  }

  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
    {!isAuthenticated ? (
      <LoginCard handleLogin={handleLogin} />
    ) : (
    <SidebarProvider defaultOpen={true}>
      <AppSidebar onTeamSelect={handleTeamSelect} />
      <SidebarInset>
        <header className="flex sticky top-0 bg-background h-14 shrink-0 items-center gap-2 border-b px-4 z-10 shadow">
          <div className="flex items-center gap-2 px-4 w-full">
            <img src={ag} alt="Banner" className="h-8" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">
                    DyoGrid
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Bench</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <div className="ml-auto hidden items-center gap-2 md:flex">
              <ModeToggle />
            </div>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          <div className="min-h-[100vh] flex-1 rounded-xl bg-muted/50 md:min-h-min">
            <Separator className="mb-4" />
            <Button onClick={runBench} disabled={running} className="mb-4">
              {running ? 'Running...' : 'Run Benchmark'}
            </Button>
            <pre className="whitespace-pre-wrap text-sm p-4">{output}</pre>
          </div>
        </div>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
    )}
    </ThemeProvider>
  );
}
