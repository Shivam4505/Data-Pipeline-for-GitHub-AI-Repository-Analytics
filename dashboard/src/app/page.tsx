'use client'

import { Suspense } from 'react'
import { DashboardOverview } from '@/components/dashboard/DashboardOverview'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'

export default function HomePage() {
    return (
        <div className="min-h-screen bg-background">
            <Sidebar />
            <div className="lg:pl-64">
                <Header />
                <main className="p-4 md:p-6 lg:p-8">
                    <Suspense fallback={<DashboardSkeleton />}>
                        <DashboardOverview />
                    </Suspense>
                </main>
            </div>
        </div>
    )
}

function DashboardSkeleton() {
    return (
        <div className="space-y-6 animate-pulse">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="metric-card">
                        <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                        <div className="h-8 bg-muted rounded w-1/2" />
                    </div>
                ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="chart-container bg-card rounded-xl border p-6" />
                <div className="chart-container bg-card rounded-xl border p-6" />
            </div>
        </div>
    )
}