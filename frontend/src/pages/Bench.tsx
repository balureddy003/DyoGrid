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
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import ag from '@/assets/ag.png';
import axios from 'axios'
import { Footer } from '@/components/Footer'
import { Agent, Team, useTeamsContext } from '@/contexts/TeamsContext';
import { toast } from 'sonner'
import { Toaster } from '@/components/ui/sonner'

function parseCsv(csv: string): Record<string, string>[] {
  const lines = csv.trim().split('\n');
  if (lines.length < 2) return [];
  const headers = lines[0].split(',');
  return lines.slice(1).map((line) => {
    const cells = line.split(',');
    const row: Record<string, string> = {};
    headers.forEach((h, i) => {
      row[h] = cells[i] ?? '';
    });
    return row;
  });
}

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
  const [results, setResults] = useState<Record<string, string>[]>([]);
  const [scenario, setScenario] = useState('scenarios/basic.jsonl');
  const [config, setConfig] = useState('');
  const [repeats, setRepeats] = useState(1);
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
      toast.info('Benchmark started');
      await axios.post(`${BASE_URL}/bench/run`, {
        scenario,
        repeats,
        ...(config ? { config } : {})
      });
      const res = await axios.get(`${BASE_URL}/bench/results`);
      setOutput(res.data.csv);
      setResults(parseCsv(res.data.csv));
      toast.success('Benchmark completed');
    } catch (err) {
      console.error(err);
      toast.error('Benchmark failed');
    } finally {
      setRunning(false);
    }
  }

  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
    <Toaster position="top-right" />
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
          <div className="min-h-[100vh] flex-1 rounded-xl bg-muted/50 md:min-h-min p-4 space-y-4">
            <Separator className="mb-4" />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="scenario">Scenario</Label>
                <Input id="scenario" value={scenario} onChange={e => setScenario(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="config">Config</Label>
                <Input id="config" value={config} onChange={e => setConfig(e.target.value)} />
              </div>
              <div className="space-y-2">
                <Label htmlFor="repeats">Repeats</Label>
                <Input id="repeats" type="number" value={repeats} onChange={e => setRepeats(parseInt(e.target.value))} />
              </div>
            </div>
            <Button onClick={runBench} disabled={running} className="mb-4">
              {running ? 'Running...' : 'Run Benchmark'}
            </Button>
            {results.length > 0 && (
              <div className="overflow-auto">
                <table className="text-sm border-collapse">
                  <thead>
                    <tr>
                      {Object.keys(results[0]).map((h) => (
                        <th key={h} className="border px-2 py-1 text-left">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row, idx) => (
                      <tr key={idx}>
                        {Object.keys(row).map((h) => (
                          <td key={h} className="border px-2 py-1">{row[h]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {!results.length && <pre className="whitespace-pre-wrap text-sm">{output}</pre>}
          </div>
        </div>
        <Footer />
      </SidebarInset>
    </SidebarProvider>
    )}
    </ThemeProvider>
  );
}
