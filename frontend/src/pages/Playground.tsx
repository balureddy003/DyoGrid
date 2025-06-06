import { useState, useEffect } from 'react'
import { AppSidebar } from "@/components/app-sidebar"
import { useUserContext } from '@/contexts/UserContext'
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
// import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Card, CardContent, CardFooter} from "@/components/ui/card"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {  ChartNoAxesCombined, CloudUpload, DollarSign, Dot, Edit, Gamepad2, Info, Loader2, SendHorizonal, ShieldAlert, ShoppingBasket, Soup, Terminal, Volleyball, Wrench, AudioWaveform, Map, MonitorCog, Globe, BookMarked, Bot, Search, DatabaseZap, User,  Target, File } from "lucide-react"
import { Button } from "@/components/ui/button"

// import remarkBreaks from 'remark-breaks'
import { Textarea } from "@/components/ui/textarea"

import { AgentsSetup } from '@/components/agents-setup';
import { MarkdownRenderer } from '@/components/markdown-display';
import { ModeToggle } from '@/components/mode-toggle'
import { LoginCard } from "@/components/login";

import axios from 'axios';

import ag from '@/assets/ag.png';

import { getAvatarSrc, getAvatarFallback } from '@/components/agents-definition'

import { Footer } from "@/components/Footer";

// If you need teams or methods:
import { Team, Agent, useTeamsContext } from '@/contexts/TeamsContext';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import React from 'react';

// Define environment variables with default values
const BASE_URL = import.meta.env.VITE_BASE_URL;
const ALLWAYS_LOGGED_IN =
  import.meta.env.VITE_ALLWAYS_LOGGED_IN === "true" ? true : false;
const ACTIVATION_CODE = import.meta.env.VITE_ACTIVATON_CODE;

console.log('BASE_URL:', BASE_URL);
console.log('ALLWAYS_LOGGED_IN:', ALLWAYS_LOGGED_IN);
// console.log('ACTIVATION_CODE:', ACTIVATION_CODE);

interface ChatMessage {
  user: string;
  message: string;
  time?: string;
  type?: string;
  source?: string;
  content?: string;
  stop_reason?: string;
  models_usage?: string;
  content_image?: string;
  session_id?: string;
  elapsed_time?: number;
}

export default function App() {

  const wellcomeMessage: ChatMessage = {
    user: 'MagenticOneOrchestrator',
    message: "My team is ready to assist you. Please type your task below to start.",
    // message: sampleMarkdown,
    time: new Date().toISOString(),
    // content: response.data.content,
    source: 'MagenticOneOrchestrator',
    session_id: 'dummy-generated-session-id',
  };
  // const debugMessages: ChatMessage[] = [
  //   {
  //     user: 'TaskResult',
  //     message: "My team is ready to assist you. Please type your task below to start.",
  //     time: new Date().toISOString(),    
  //     source: 'MagenticOneOrchestrator',
  //     session_id: 'dummy-generated-session-id',
  //   },
  //   {
  //     user: 'User',
  //     message: "Hello! How can I assist you today?",       
  //     time: new Date().toISOString(),
  //     source: 'Coder',
  //     session_id: 'dummy-generated-session-id',
  //   },
  // ]

  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([wellcomeMessage]);
  // const [chatHistory, setChatHistory] = useState<ChatMessage[]>(debugMessages);

  const [sessionID, setSessionID] = useState('')
  const [userMessage, setUserMessage] = useState('')
  const [sessionTime, setSessionTime] = useState('')
  // const [files, setFiles] = useState<{ name: string, size: number, date: string }[]>([])
  const [isAuthenticated, setIsAuthenticated] = useState(ALLWAYS_LOGGED_IN)
  // const [fileUpload, setFileUpload] = useState<File | null>(null)
  // const [isFileCardVisible, setIsFileCardVisible] = useState(false)
  // const [isSettingsCardVisible, setIsSettingsCardVisible] = useState(false)
  const [isTyping, setIsTyping] = useState(false);
  const { userInfo } = useUserContext();
  // const { teams } = useTeamsContext();
  const { teams, loading, reloadTeams } = useTeamsContext();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  // Initialize agents from default team (will be updated by sidebar selection)
  // Optionally use an effect to set initial team agents if needed

  const handleTeamSelect = (team: Team) => {
    setAgents(team.agents);
    setSelectedTeam(team);
  }
  
  // Set initial team once teams are loaded
  useEffect(() => {
    if (!loading && teams.length > 0 && selectedTeam === null) {
      setSelectedTeam(teams[0]);
      setAgents(teams[0].agents);
    }
  }, [loading, teams, selectedTeam]);

  // Propagate team changes from TeamsContext to Playground local state
  useEffect(() => {
    if (!selectedTeam) return;
    const updatedTeam = teams.find(team => team.name === selectedTeam.name);
    if (updatedTeam) {
      setSelectedTeam(updatedTeam);
      setAgents(updatedTeam.agents);
    }
    console.log('Selected team in play:', selectedTeam.name);
  }, [teams, selectedTeam?.name]);

  const stopSession = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/stop?session_id=${encodeURIComponent(sessionID)}`);
      console.log('Stop session response:', response.data);
      setIsTyping(false);
      setSessionID('');
      setSessionTime('');
      // reload the page
      window.location.reload(); 
      // return response
    } catch (error) {
      console.error('Stop session error:', error);
    }
  };
  

  const handleSendStreamingMessage = async () => {
    if (!userMessage.trim()) return;
    setIsTyping(true);
    const newMessage = { user: 'User', message: userMessage };
    setChatHistory([...chatHistory, newMessage]);
    // Start timer
    const startTime = Date.now();

    // Use updated agents state directly
    const selectedAgents = agents;
    console.log('Using agents:', selectedAgents);

    try {
      const response = await axios.post(`${BASE_URL}/start`, { 
        content: userMessage, 
        user_id: userInfo.email, // Use directly from context
        agents: JSON.stringify(selectedAgents)
      });
      const sessionId = response.data.response;  // Get the session ID from the response
      setSessionID(sessionId);
      const eventSource = new EventSource(`${BASE_URL}/chat-stream?session_id=${encodeURIComponent(sessionId)}&user_id=${encodeURIComponent(userInfo.email)}`);
      eventSource.onmessage = (event) => {
        // console.log('EventSource message:', event.data);
        const data = JSON.parse(event.data);
        if (data.stop_reason) {
          setIsTyping(false);
          // Measure elapsed time and set sessionTime (assumes sessionTime state exists)
          const elapsedTime = Date.now() - startTime;
          const minutes = Math.floor(elapsedTime / 60000);
          const seconds = Math.floor((elapsedTime % 60000) / 1000);
          setSessionTime(`${minutes}:${seconds < 10 ? '0' : ''}${seconds}`);
          // eventSource.close();
        }


        const aiMessage: ChatMessage = {
          user: data.source,
          message: data.content,
          time: data.time,
          // content: data.content,
          source: data.source,
          stop_reason: data.stop_reason,
          models_usage: data.models_usage,
          content_image: data.content_image,
          session_id: data.session_id,
          elapsed_time: data.elapsed_time,
        };
  
        setChatHistory((prev) => [...prev, aiMessage]);
      };
  
      eventSource.onerror = (error) => {
        setIsTyping(false);
        console.error('EventSource error:', error);
        eventSource.close();
      };
    } catch (error) {
      console.error('Chat error:', error);
    }
    setUserMessage('');
  };

  /// TODO: better login -> MS EntraID
  const handleLogin = (email: string, password: string) => {
    console.log('Logging in with:', email)
    if (password === ACTIVATION_CODE || ALLWAYS_LOGGED_IN) {
      setIsAuthenticated(true)
    } else {
      console.log('Invalid activation code')
    }
  }

  // const handleLogout = () => {
  //   setIsAuthenticated(false)
  // }

  // Icon options for selection (updated)
  const iconOptions = [
    { value: 'Soup', label: 'Soup', icon: Soup },
    { value: 'Volleyball', label: 'Football', icon: Volleyball },
    { value: 'ChartNoAxesCombined', label: 'Market assessment', icon: ChartNoAxesCombined },
    { value: 'Wrench', label: 'Predictive Maintenance', icon: Wrench },
    { value: 'ShieldAlert', label: 'Safety', icon: ShieldAlert },
    { value: 'DollarSign', label: 'Loan Upsell', icon: DollarSign },
    { value: 'ShoppingBasket', label: 'Retail', icon: ShoppingBasket },
    { value: 'Gamepad2', label: 'Gaming', icon: Gamepad2 },
    { value: 'Terminal', label: 'Generate script', icon: Terminal },
    { value: 'AudioWaveform', label: 'Audio', icon: AudioWaveform },
    { value: 'Map', label: 'Map', icon: Map },
    { value: 'MonitorCog', label: 'Monitor', icon: MonitorCog },
    { value: 'Globe', label: 'Web', icon: Globe },
    { value: 'File', label: 'File', icon: File },
    { value: 'BookMarked', label: 'Bookmark', icon: BookMarked },
    { value: 'Bot', label: 'Bot', icon: Bot },
    { value: 'Search', label: 'Search', icon: Search },
    { value: 'ChartNoAxesCombined', label: 'ChartNoAxesCombined', icon: ChartNoAxesCombined },
    { value: 'DatabaseZap', label: 'DatabaseZap', icon: DatabaseZap },
    { value: 'MagenticOneOrchestrator', label: 'MagenticOneOrchestrator', icon: Bot },
    { value: 'User', label: 'User', icon: User },
    { value: 'TaskResult', label: 'TaskResult', icon: Target },
  ];

  // Helper to get icon component by logo string
  const getTaskLogoIcon = (logo: string | undefined) => {
    if (!logo) return null;
    const found = iconOptions.find(opt => opt.value === logo);
    if (found) {
      const Icon = found.icon;
      return <Icon className="inline mr-1 h-4 w-4 align-text-bottom" />;}
    return null;
  };

  // Dialog state for teams initialization
  const [showTeamsDialog, setShowTeamsDialog] = useState(false);

  // Show dialog if teams is empty and not loading
  useEffect(() => {
    if (!loading && teams.length === 0) {
      setShowTeamsDialog(true);
    } else {
      setShowTeamsDialog(false);
    }
  }, [loading, teams]);

  // Handlers for dialog actions
  const handleInitializeTeams = async () => {
    try {
      await axios.post(`${BASE_URL}/inititalize-teams`);
      // Reload teams list
      await reloadTeams();
      setShowTeamsDialog(false);

      // window.location.reload();
    } catch (error) {
      console.error('Failed to initialize teams:', error);
    }
  };

  // Function to get Agent by name from selectedTeam
  const getAgentByName = (name: string): Agent | undefined => {
    if (!selectedTeam) return undefined;
    // add special case for MagenticOneOrchestrator
    if (name === 'MagenticOneOrchestrator') {
      return { input_key: "", type: "",name: "MagenticOneOrchestrator",system_message: "",description: "",icon: "MagenticOneOrchestrator",index_name: ""}
    }
    // add special case for User
    if (name=== 'User') {
      return {input_key: "",type: "",name: "User",system_message: "",description: "",icon: "User", index_name: ""}
    } 
    // add special case for TaskResult
    if (name=== 'TaskResult') {
      return {input_key: "",type: "",name: "TaskResult",system_message: "",description: "",icon: "TaskResult",index_name: ""}
    }
    // Check if selectedTeam is defined and has agents
    return selectedTeam.agents.find(agent => agent.name === name);
  };

  if (!loading && teams.length === 0) {
    return (
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <SidebarProvider defaultOpen={true}>
          <AppSidebar onTeamSelect={handleTeamSelect} />
          <SidebarInset>
            <div className="flex items-center justify-center h-40">
              <Loader2 className="h-8 w-8 animate-spin" /> Empty teams...
              {/* Teams empty dialog */}
              <Dialog open={showTeamsDialog}>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>
                      <ShieldAlert className="mr-2 inline h-12 w-12 text-red-500" />
                      Looks like you have no teams.
                    </DialogTitle>
                  </DialogHeader>
                  <DialogFooter className="flex flex-row gap-2 justify-end">
                    <Button variant="destructive" onClick={handleInitializeTeams}><CloudUpload /> Initialize</Button>
                    <Button asChild variant="outline">
                      <a href="/agents"><Edit />Create your own</a>
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </div>
          </SidebarInset>
        </SidebarProvider>
      </ThemeProvider>
    );
  }
  else if (loading || !selectedTeam) {
    return (
      <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
        <SidebarProvider defaultOpen={true}>
          <AppSidebar onTeamSelect={handleTeamSelect} />
          <SidebarInset>
            <div className="flex items-center justify-center h-40">
              <Loader2 className="h-8 w-8 animate-spin" /> Loading teams...
            </div>
          </SidebarInset>
        </SidebarProvider>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
      
      {/* Main content */}
      {!isAuthenticated ? (
        <LoginCard handleLogin={handleLogin} />
      ) : (
      <SidebarProvider defaultOpen={true}>
        <AppSidebar onTeamSelect={handleTeamSelect} /> {/* Remove onUserNameChange prop */}
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
                    <BreadcrumbPage>Playground</BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <div className="ml-auto hidden items-center gap-2 md:flex">
     
              {/* if the session end display elapsed time */}
              <div className="flex gap-0 p-0 pt-0 justify-end">
                {sessionTime && !isTyping ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <p className='text-sm text-muted-foreground'>Session {sessionID} completed in {sessionTime}s.</p>
                    <Button variant="secondary" onClick={() => stopSession()}>
                      Run new
                    </Button>
                  </div>
                ) : null}
                {isTyping ? (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <p className='text-sm text-muted-foreground'>Running {sessionID} session...</p>
                    <Loader2 className="lucide lucide-loader2 mr-2 h-4 animate-spin loader-green" />
                    {/* button to stop the session */}
                    <Button variant="destructive" onClick={() => stopSession()}>Stop</Button>
                  </div>
                ) : <p className='text-sm text-muted-foreground loader-green'></p>}
              </div>
        
   
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
            <Separator  />
            {/* Agents setup */}
            <AgentsSetup
                team={selectedTeam}
                getAvatarSrc={getAvatarSrc}
                isCollapsed={isTyping || (sessionTime) ? true : false}
                showDetails={false}
              />
             {/* if session is running display loader */}
            <div className="min-h-[100vh] flex-1 rounded-xl bg-muted/50 md:min-h-min">
              {/* Chat Interface */}
              <Card className={`md:col-span-2 h-full flex flex-col`}>
                <CardContent className="flex-1 h-96">
                  <Separator className='my-2 invisible'/>
                  <div className="space-y-4">
                    {chatHistory.map((message, index) => (
                      <div key={index} className={`flex ${message.user === 'User' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`p-2 rounded-lg shadow ${message.user === 'User' ? 'group/message relative break-words rounded-lg p-3 text-sm sm:max-w-[70%] bg-primary text-primary-foreground duration-300 animate-in fade-in-0 zoom-in-75 origin-bottom-right' : 'group/message relative break-words rounded-lg p-3 text-sm sm:max-w-[96%] bg-muted text-foreground duration-300 animate-in fade-in-0 zoom-in-75 origin-bottom-left'}`}>
                          <div className="flex items-center space-x-2">
                            <Avatar>
                              <AvatarFallback>
                                {(() => {
                                  const agent = getAgentByName(message.user);
                                  if (agent && agent.icon) {
                                    const iconOpt = iconOptions.find(opt => opt.value === agent.icon);
                                    // Only render if iconOpt.icon is a Lucide icon (function, not native File constructor)
                                    if (iconOpt) {
                                      return React.createElement(iconOpt.icon, { className: 'h-5 w-5' });
                                    }
                                  }
                                  return getAvatarFallback(message.user);
                                })()}
                              </AvatarFallback>

                              {/* <Bot className="ml-autoaspect-square h-full w-full" /> */}
                            </Avatar>
                            <div className="break-all max-w-[100%] message">
                              <p className="text-sm font-semibold">{message.user}</p>
                              <MarkdownRenderer markdownText={message.message} />
                              {/* Display image if available */}
                              {message.content_image && (
                                <img src={`${message.content_image}`} alt="content" className="mt-2 max-w-[625px]" />
                              )}
                              {/* <MarkdownRenderer>{message.message}</MarkdownRenderer> */}
                              <p className="text-xs text-muted-foreground">{message.time && new Date(message.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit',hour12: false })}</p>
                            </div>
                          </div>
                        </div>
                       {/* <div className='inline'>
                        <time className=" mt-1 block px-1 text-xs opacity-50 duration-500 animate-in fade-in-0">
                          {message.time && new Date(message.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}
                        </time>
                       </div> */}
                      </div>
                    ))}

                    
                    {isTyping ? (
                      <div className="justify-left flex space-x-1">
                        <div className="rounded-lg bg-muted p-3 shadow">
                          <div className="flex -space-x-2.5">
                          <Dot className='lucide lucide-dot h-5 w-5 animate-typing-dot-bounce' />
                          <Dot className='lucide lucide-dot h-5 w-5 animate-typing-dot-bounce [animation-delay:90ms]' />
                          <Dot className='lucide lucide-dot h-5 w-5 animate-typing-dot-bounce [animation-delay:180ms]' />
                          </div>
                        </div>
                      </div>
                    ) : null}
                  </div>
                </CardContent>
                <CardFooter className="flex flex-col space-y-2">
                  <div className="relative w-full">
                    <Textarea
                      value={userMessage}
                      onChange={(e) => setUserMessage(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          handleSendStreamingMessage();
                        }
                      }}
                      placeholder="Type a message..."
                      className="z-10 w-full h-36 grow resize-none rounded-xl border border-input bg-background p-3 pr-24 text-sm ring-offset-background transition-[border] placeholder:text-muted-foreground focus-visible:border-primary focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-50"
                      disabled={isTyping}
                    />
                    <Button 
                      onClick={handleSendStreamingMessage} 
                      disabled={isTyping}
                      className="absolute bottom-2 right-2"
                    >
                      <SendHorizonal />
                    </Button>
                  </div>
                  <div className="relative w-full">
                    <p className="text-xs text-muted-foreground">
                      <Info className="mr-1 inline h-4 w-4" />
                        AI-generated content may be incorrect.
                    </p>
                  </div>
                  <div className="flex space-x-2">
                      {selectedTeam.starting_tasks?.map(task => (
                          <Button
                              key={task.id} 
                              variant="outline"
                              className="text-sm bg-muted"
                              onClick={() => setUserMessage(task.prompt)}
                          >
                              {getTaskLogoIcon(task.logo)} {task.name}
                          </Button>
                      ))}
                  </div>
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
  )
}
