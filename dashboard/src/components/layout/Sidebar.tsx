'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
    LayoutDashboard,
    Database,
    TrendingUp,
    Users,
    Activity,
    Settings,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react'
import { clsx } from 'clsx'
import { useState } from 'react'

const navigation = [
    { name: 'Overview', href: '/', icon: LayoutDashboard },
    { name: 'Repositories', href: '/repositories', icon: Database },
    { name: 'Trends', href: '/trends', icon: TrendingUp },
    { name: 'Contributors', href: '/contributors', icon: Users },
    { name: 'Activity', href: '/activity', icon: Activity },
    { name: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
    const pathname = usePathname()
    const [collapsed, setCollapsed] = useState(false)

    return (
        <aside
            className={clsx(
                'fixed left-0 top-0 z-40 h-screen bg-card border-r transition-all duration-300',
                collapsed ? 'w-16' : 'w-64'
            )}
        >
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div
                    className={clsx(
                        'flex h-16 items-center justify-between px-4 border-b',
                        collapsed && 'justify-center'
                    )}
                >
                    {!collapsed && (
                        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary">
                            <LayoutDashboard className="h-6 w-6" />
                            <span>GitHub AI Analytics</span>
                        </Link>
                    )}
                    <button
                        onClick={() => setCollapsed(!collapsed)}
                        className={clsx(
                            'p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors',
                            collapsed && 'mx-auto'
                        )}
                        aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                    >
                        {collapsed ? <ChevronRight className="h-5 w-5" /> : <ChevronLeft className="h-5 w-5" />}
                    </button>
                </div>

                {/* Navigation */}
                <nav className="flex-1 p-4 space-y-1 overflow-y-auto" aria-label="Main navigation">
                    {navigation.map((item) => {
                        const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
                        return (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={clsx(
                                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                                    isActive
                                        ? 'bg-primary text-primary-foreground'
                                        : 'text-muted-foreground hover:bg-accent hover:text-foreground',
                                    collapsed && 'justify-center'
                                )}
                                aria-current={isActive ? 'page' : undefined}
                                title={collapsed ? item.name : undefined}
                            >
                                <item.icon className="h-5 w-5 flex-shrink-0" aria-hidden="true" />
                                {!collapsed && <span>{item.name}</span>}
                            </Link>
                        )
                    })}
                </nav>

                {/* Footer */}
                <div className={clsx('p-4 border-t', collapsed && 'hidden')}>
                    <div className="text-xs text-muted-foreground text-center">
                        GitHub AI Analytics v1.0.0
                    </div>
                </div>
            </div>
        </aside>
    )
}