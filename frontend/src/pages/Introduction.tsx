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
import { Card, CardHeader,CardContent, CardFooter} from "@/components/ui/card"

export default function Introduction() {
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
                  <h1 className="text-2xl font-bold mb-2">Build your dream team with Autogen</h1>
                </CardHeader>
                <CardContent className="flex-1 space-y-6">
                  <p className="text-base">
                    This repository is a part of the <span className="font-semibold">Azure Samples</span> collection and utilizes <span className="font-semibold">Microsoft Autogen 0.4</span> alongside <span className="font-semibold">Azure OpenAI</span>.<br/>
                    It seamlessly integrates with a <span className="font-semibold">React UI</span> to create a comprehensive end-to-end multi-agent application.<br/>
                    Designed for simplicity, this repository streamlines the process of building, testing, and deploying an advanced multi-agent framework.
                    <a href="https://www.microsoft.com/en-us/research/articles/magentic-one-a-generalist-multi-agent-system-for-solving-complex-tasks/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline ml-1">Magentic One</a>
                  </p>
                  <div className="flex justify-center my-4">
                    <img
                      src="https://raw.githubusercontent.com/Azure-Samples/dream-team/main/assets/architecture.png"
                      alt="Architecture"
                      className="rounded-lg shadow max-w-[60%] h-auto"
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <span role="img" aria-label="tada">🎉</span>
                      <span className="font-semibold">February 25, 2025:</span>
                      <span>We have a new React based UI with new business use cases</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span role="img" aria-label="tada">🎉</span>
                      <span className="font-semibold">January 11, 2025:</span>
                      <span>The repo now supports <a href="https://microsoft.github.io/autogen/stable/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Autogen 0.4.0 stable version</a></span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span role="img" aria-label="tada">🎉</span>
                      <span className="font-semibold">December 3, 2024:</span>
                      <span>The repo now supports one click deployment with <a href="https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Azure Developer CLI</a>, if you would like to run it with the full process locally you can check <a href="https://github.com/yanivvak/dream-team/tree/v0.21" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">v0.21</a></span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span role="img" aria-label="tada">🎉</span>
                      <span className="font-semibold">November 18, 2024:</span>
                      <span>We are porting this repo to <a href="https://microsoft.github.io/autogen/0.4.0.dev6/index.html" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Autogen 0.4</a>, a new event driven, asynchronous architecture for AutoGen and <a href="https://github.com/microsoft/autogen/tree/main/python/packages/autogen-magentic-one" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">Magentic One</a></span>
                    </div>
                  </div>
                  <div className="mt-4">
                    {/* Replaced link with video component */}
                    <video
                      controls
                      className="rounded-lg shadow max-w-full h-auto"
                      src="https://github.com/user-attachments/assets/e3f1bbae-a93b-47d8-b661-b6a9507c243b"
                    >
                      Your browser does not support the video tag.
                    </video>
                  </div>
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
