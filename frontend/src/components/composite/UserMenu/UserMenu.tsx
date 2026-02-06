import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { useAuth } from '@/contexts/AuthContext'
import { cn } from '@/lib/utils'
import PersonIcon from '@mui/icons-material/Person'
import SettingsIcon from '@mui/icons-material/Settings'
import LogoutIcon from '@mui/icons-material/Logout'

export interface UserMenuProps {
  /** Additional class names */
  className?: string
}

export function UserMenu({ className }: UserMenuProps) {
  const { user, signOut } = useAuth()

  const initials = user?.email
    ? user.email.substring(0, 2).toUpperCase()
    : '?'

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Sign out failed:', error)
    }
  }

  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button
          className={cn(
            'flex items-center justify-center w-10 h-10 rounded-full',
            'bg-apple-gray text-apple-text-secondary font-medium text-sm',
            'hover:bg-gray-200 transition-colors',
            'focus-visible:ring-2 focus-visible:ring-apple-blue focus-visible:ring-offset-2',
            'min-w-[44px] min-h-[44px]', // WCAG 2.5.8 touch target
            className
          )}
          aria-label={`User menu for ${user?.email || 'user'}`}
        >
          {initials}
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content
          className={cn(
            'min-w-[200px] bg-white rounded-xl p-1',
            'shadow-[0_10px_40px_-5px_rgba(0,0,0,0.1),0_0_1px_rgba(0,0,0,0.1)]',
            'animate-scale-in origin-top-right',
            'z-50'
          )}
          sideOffset={8}
          align="end"
        >
          {/* User info header */}
          <div className="px-3 py-2 border-b border-apple-border mb-1">
            <p className="text-sm font-medium text-apple-text truncate">
              {user?.email}
            </p>
          </div>

          {/* Menu items */}
          <DropdownMenu.Item
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
              'text-sm text-apple-text-secondary',
              'hover:bg-apple-gray hover:text-apple-text',
              'focus:bg-apple-gray focus:text-apple-text focus:outline-none',
              'transition-colors'
            )}
          >
            <PersonIcon className="w-4 h-4" />
            Profile
          </DropdownMenu.Item>

          <DropdownMenu.Item
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
              'text-sm text-apple-text-secondary',
              'hover:bg-apple-gray hover:text-apple-text',
              'focus:bg-apple-gray focus:text-apple-text focus:outline-none',
              'transition-colors'
            )}
          >
            <SettingsIcon className="w-4 h-4" />
            Settings
          </DropdownMenu.Item>

          <DropdownMenu.Separator className="h-px bg-apple-border my-1" />

          <DropdownMenu.Item
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer',
              'text-sm text-apple-red',
              'hover:bg-red-50',
              'focus:bg-red-50 focus:outline-none',
              'transition-colors'
            )}
            onSelect={handleSignOut}
          >
            <LogoutIcon className="w-4 h-4" />
            Sign Out
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  )
}
