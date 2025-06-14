import { AppSidebar } from '@/components/app-sidebar'
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar'
import { ThemeProvider } from '@/components/theme-provider'

const MCP_GATEWAY_URL =
  import.meta.env.VITE_MCP_GATEWAY_URL || 'http://localhost:8000/mcp'

export default function McpGateway() {
  return (
    <ThemeProvider defaultTheme="light" storageKey="vite-ui-theme">
      <SidebarProvider defaultOpen={true}>
        <AppSidebar onTeamSelect={() => {}} />
        <SidebarInset>
          <iframe
            src={`${MCP_GATEWAY_URL}/admin`}
            style={{ width: '100%', height: '100%', border: '0' }}
            title="MCP Gateway"
          />
        </SidebarInset>
      </SidebarProvider>
    </ThemeProvider>
  )
}
