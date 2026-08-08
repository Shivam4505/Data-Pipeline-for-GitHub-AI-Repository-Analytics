'use client'

import { Menu, Sun, Moon, Bell, Search, User, LogOut, ChevronDown } from 'lucide-react'
import { useState } from 'react'
import Link from 'next/link'
import { clsx } from 'clsx'

export function Header() {
    const [darkMode, setDarkMode] = useState(false)
    const [userMenuOpen, setUserMenuOpen] = useState(false)
    const [searchQuery, setSearchQuery] = useState('')

    const toggleDarkMode = () => {
        setDarkMode(!darkMode)
        document.documentElement.classList.toggle('dark')
    }

    return (
        <header className="sticky top-0 z-30 h-16 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b">
            <div className="flex h-full items-center justify-between px-4 md:px-6">
                {/* Left side - Mobile menu button */}
                <div className="flex items-center gap-4 lg:hidden">
                    <button
                        className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                        aria-label="Open menu"
                    >
                        <Menu className="h-5 w-5" />
                    </button>
                </div>

                {/* Center - Search */}
                <div className="hidden md:flex flex-1 max-w-md mx-4 md:mx-8">
                    <div className="relative w-full">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <input
                            type="search"
                            placeholder="Search repositories, topics, contributors..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full h-10 pl-10 pr-4 rounded-lg bg-muted/50 border border-border/50 text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                            aria-label="Search"
                        />
                    </div>
                </div>

                {/* Right side - Actions */}
                <div className="flex items-center gap-2">
                    {/* Dark mode toggle */}
                    <button
                        onClick={toggleDarkMode}
                        className="p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                        aria-label={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
                    >
                        {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                    </button>

                    {/* Notifications */}
                    <button className="relative p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors" aria-label="Notifications">
                        <Bell className="h-5 w-5" />
                        <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-red-500" />
                    </button>

                    {/* User menu */}
                    <div className="relative">
                        <button
                            onClick={() => setUserMenuOpen(!userMenuOpen)}
                            className="flex items-center gap-2 p-2 rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
                            aria-label="User menu"
                            aria-expanded={userMenuOpen}
                        >
                            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center">
                                <User className="h-5 w-5 text-primary" />
                            </div>
                            <span className="hidden md:block font-medium">User</span>
                            <ChevronDown className="h-4 w-4" />
                        </button>

                        {userMenuOpen && (
                            <div className="absolute right-0 mt-2 w-48 bg-card border rounded-xl shadow-lg py-2 animate-slide-up">
                                <Link
                                    href="/profile"
                                    className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground"
                                    onClick={() => setUserMenuOpen(false)}
                                >
                                    <User className="h-4 w-4" />
                                    Profile
                                </Link>
                                <Link
                                    href="/settings"
                                    className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:bg-accent hover:text-foreground"
                                    onClick={() => setUserMenuOpen(false)}
                                >
                                    <Sun className="h-4 w-4" />
                                    Settings
                                </Link>
                                <hr className="my-2 border-border" />
                                <button
                                    className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-accent"
                                    onClick={() => setUserMenuOpen(false)}
                                >
                                    <LogOut className="h-4 w-4" />
                                    Sign out
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}