import {useState } from 'react'
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
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import { ThemeProvider } from "@/components/theme-provider"
import { ModeToggle } from '@/components/mode-toggle'
import { LoginCard } from "@/components/login";
import ag from '@/assets/ag.png';


// TODO: FUJ! How to get ENV vars from SWA?
// Define environment variables with default values
const BASE_URL = import.meta.env.VITE_BASE_URL || "local";
const ALLWAYS_LOGGED_IN =
  import.meta.env.VITE_ALLWAYS_LOGGED_IN === "true" ? true : false;
const ACTIVATION_CODE = import.meta.env.VITE_ACTIVATON_CODE || "0000";

// console.log('VITE_BASE_URL:', BASE_URL);
// console.log('VITE_ALLWAYS_LOGGED_IN:', ALLWAYS_LOGGED_IN);
// console.log('VITE_ACTIVATON_CODE:', ACTIVATION_CODE);

import { Footer } from '@/components/Footer'

import { Agent, Team, useTeamsContext } from '@/contexts/TeamsContext';
import { AlarmClock } from 'lucide-react'
import { Card, CardHeader,CardContent, CardFooter} from "@/components/ui/card"

export default function GeneralSettings() {
  const { teams} = useTeamsContext();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team>(teams[0]);
  const [isAuthenticated, setIsAuthenticated] = useState(BASE_URL)

  /// TODO: better login -> MS EntraID
  const handleLogin = (email: string, password: string) => {
    console.log('Logging in with:', email)
    if (password === ACTIVATION_CODE || ALLWAYS_LOGGED_IN) {
      setIsAuthenticated(true)
    } else {
      console.log('Invalid activation code')
    }
  }
  const handleTeamSelect = (team: Team) => {
    setAgents(team.agents);
    setSelectedTeam(team);
    console.log('Selected team:', selectedTeam.name);
    console.log('Selected agents:', agents);
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
            {/* <img src={banner} alt="Banner" className="h-64" /> */}
            {/* <SidebarTrigger />   */}
            {/* <Bot className="h-8 w-8" /> */}
            <img src={ag  } alt="Banner" className="h-8" />
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
                  <BreadcrumbPage>Library</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
            <div className="ml-auto hidden items-center gap-2 md:flex">
        
   
            {/* <Separator orientation="vertical" className="mr-2 h-4" /> */}
            <ModeToggle />
            {/* <Separator orientation="vertical" className="mr-2 h-4" /> */}
            {/* {isAuthenticated ? (
              <Button variant="outline" onClick={handleLogout}>
                <LogOut />Log out
              </Button>
            ) : null} */}
                
            </div>
          </div>
        </header>
        {/* Main content */}
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
            <div className="min-h-[100vh] flex-1 rounded-xl bg-muted/50 md:min-h-min">
            <Separator className="mb-4" />
        
            <Card className={`md:col-span-2 h-full flex flex-col`}>
                <CardHeader>
                    <AlarmClock className="h-8 w-8" />
                </CardHeader>
                <CardContent className="flex-1">
                    <h2 className="text-lg font-bold">Comming soon...</h2>
                    <p>
                      This is a placeholder for the Introduction documentation page.
                      The content will be updated soon.
                    </p>
                </CardContent>
                <CardFooter>
                    <p className="text-sm text-muted-foreground">
                      AI-generated content may be incorrect.
                    </p>
                </CardFooter>
            </Card>
       
            </div>
        </div>
        {/* Footer */}
      <Footer />
      </SidebarInset>
    </SidebarProvider>
    )}
    </ThemeProvider>
  );
}
