import { useState } from 'react'
import { AppSidebar } from '@/components/app-sidebar'
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import {
  SidebarInset,
  SidebarProvider,
} from '@/components/ui/sidebar'
import { ThemeProvider } from '@/components/theme-provider'
import { ModeToggle } from '@/components/mode-toggle'
import { LoginCard } from '@/components/login'
import ag from '@/assets/ag.png'

const BASE_URL = import.meta.env.VITE_BASE_URL || 'local'
const ALLWAYS_LOGGED_IN = import.meta.env.VITE_ALLWAYS_LOGGED_IN === 'true' ? true : false
const ACTIVATION_CODE = import.meta.env.VITE_ACTIVATON_CODE || '0000'

import { Footer } from '@/components/Footer'
import axios from 'axios'
import { Agent, Team, useTeamsContext } from '@/contexts/TeamsContext'

export default function Tools() {
  const { teams } = useTeamsContext()
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedTeam, setSelectedTeam] = useState<Team>(teams[0])
  const [isAuthenticated, setIsAuthenticated] = useState(BASE_URL)

  const handleLogin = (email: string, password: string) => {
    if (password === ACTIVATION_CODE || ALLWAYS_LOGGED_IN) {
      setIsAuthenticated(true)
    }
  }
  const handleTeamSelect = (team: Team) => {
    setAgents(team.agents)
    setSelectedTeam(team)
  }

  const [calcA, setCalcA] = useState('')
  const [calcB, setCalcB] = useState('')
  const [calcOp, setCalcOp] = useState('+')
  const [calcResult, setCalcResult] = useState('')

  const runCalculator = async () => {
    const res = await axios.post(`${BASE_URL}/tools/calculator`, {
      a: parseFloat(calcA),
      b: parseFloat(calcB),
      operator: calcOp,
    })
    setCalcResult(res.data.result)
  }

  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<any[]>([])

  const runSearch = async () => {
    const res = await axios.post(`${BASE_URL}/tools/google_search`, {
      query: searchQuery,
      num_results: 3,
    })
    setSearchResults(res.data)
  }

  const [webUrl, setWebUrl] = useState('')
  const [webContent, setWebContent] = useState('')

  const runFetchWebpage = async () => {
    const res = await axios.post(`${BASE_URL}/tools/fetch_webpage`, { url: webUrl })
    setWebContent(res.data.content)
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
                      <BreadcrumbLink href="#">DyoGrid</BreadcrumbLink>
                    </BreadcrumbItem>
                    <BreadcrumbSeparator className="hidden md:block" />
                    <BreadcrumbItem>
                      <BreadcrumbPage>Tools</BreadcrumbPage>
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
                <div className="p-4 space-y-6">
                  <div>
                    <h3 className="font-bold mb-2">Calculator</h3>
                    <input className="border mr-2" value={calcA} onChange={e => setCalcA(e.target.value)} placeholder="A" />
                    <input className="border mx-2" value={calcB} onChange={e => setCalcB(e.target.value)} placeholder="B" />
                    <input className="border mr-2" value={calcOp} onChange={e => setCalcOp(e.target.value)} placeholder="op" />
                    <button className="border px-2" onClick={runCalculator}>Run</button>
                    {calcResult && <div>Result: {calcResult}</div>}
                  </div>
                  <div>
                    <h3 className="font-bold mb-2">Google Search</h3>
                    <input className="border mr-2" value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="query" />
                    <button className="border px-2" onClick={runSearch}>Search</button>
                    <ul>
                      {searchResults.map((r, idx) => (
                        <li key={idx}><a href={r.link}>{r.title}</a></li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-bold mb-2">Fetch Webpage</h3>
                    <input className="border mr-2" value={webUrl} onChange={e => setWebUrl(e.target.value)} placeholder="url" />
                    <button className="border px-2" onClick={runFetchWebpage}>Fetch</button>
                    {webContent && <pre className="mt-2 whitespace-pre-wrap text-sm">{webContent}</pre>}
                  </div>
                </div>
              </div>
            </div>
            <Footer />
          </SidebarInset>
        </SidebarProvider>
      )}
    </ThemeProvider>
  )
}
