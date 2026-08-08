'use client'

import { useQuery } from '@tanstack/react-query'
import {
    LineChart,
    Line,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ComposedChart,
} from 'recharts'
import {
    Database,
    Users,
    GitBranch,
    Star,
    TrendingUp,
    Clock,
    ExternalLink,
} from 'lucide-react'
import { format, subDays, startOfDay } from 'date-fns'
import { clsx } from 'clsx'

// Types
interface SummaryStats {
    total_repositories: number
    total_ai_ml_repositories: number
    total_contributors: number
    total_commits: number
    total_stars: number
    total_forks: number
    total_issues: number
    total_prs: number
    total_prs_merged: number
    top_languages: Array<{ language: string; count: number }>
    top_topics: Array<{ topic: string; count: number }>
    recent_activity: Array<{ date: string; commits: number; prs: number; issues: number }>
    top_repositories: Array<{ id: number; full_name: string; stars: number; language: string }>
    top_contributors: Array<{ login: string; commits: number; avatar_url: string }>
}

interface ActivityDataPoint {
    date: string
    commits_count: number
    additions: number
    deletions: number
    prs_opened: number
    prs_merged: number
    issues_opened: number
    issues_closed: number
    stars_gained: number
}

interface LanguageTrend {
    date: string
    language: string
    repo_count: number
    total_stars: number
}

// Mock data generators
function generateMockSummaryStats(): SummaryStats {
    return {
        total_repositories: 1247,
        total_ai_ml_repositories: 892,
        total_contributors: 15634,
        total_commits: 2847391,
        total_stars: 4521839,
        total_forks: 678234,
        total_issues: 123456,
        total_prs: 89234,
        total_prs_merged: 67123,
        top_languages: [
            { language: 'Python', count: 542 },
            { language: 'TypeScript', count: 187 },
            { language: 'C++', count: 134 },
            { language: 'Jupyter Notebook', count: 98 },
            { language: 'Rust', count: 67 },
            { language: 'Go', count: 54 },
            { language: 'JavaScript', count: 43 },
            { language: 'Julia', count: 21 },
        ],
        top_topics: [
            { topic: 'machine-learning', count: 423 },
            { topic: 'deep-learning', count: 312 },
            { topic: 'nlp', count: 198 },
            { topic: 'computer-vision', count: 176 },
            { topic: 'llm', count: 145 },
            { topic: 'transformers', count: 134 },
            { topic: 'pytorch', count: 123 },
            { topic: 'tensorflow', count: 112 },
        ],
        recent_activity: Array.from({ length: 30 }, (_, i) => ({
            date: format(subDays(new Date(), 29 - i), 'yyyy-MM-dd'),
            commits: Math.floor(Math.random() * 5000) + 1000,
            prs: Math.floor(Math.random() * 500) + 100,
            issues: Math.floor(Math.random() * 300) + 50,
        })),
        top_repositories: [
            { id: 1, full_name: 'pytorch/pytorch', stars: 72000, language: 'C++' },
            { id: 2, full_name: 'tensorflow/tensorflow', stars: 178000, language: 'C++' },
            { id: 3, full_name: 'huggingface/transformers', stars: 115000, language: 'Python' },
            { id: 4, full_name: 'langchain-ai/langchain', stars: 89000, language: 'Python' },
            { id: 5, full_name: 'openai/gym', stars: 32000, language: 'Python' },
        ],
        top_contributors: [
            { login: 'soumith', commits: 2847, avatar_url: 'https://github.com/soumith.png' },
            { login: 'jerry-git', commits: 1923, avatar_url: 'https://github.com/jerry-git.png' },
            { login: 'apaszke', commits: 1654, avatar_url: 'https://github.com/apaszke.png' },
            { login: 'thomwolf', commits: 1432, avatar_url: 'https://github.com/thomwolf.png' },
            { login: 'huggingface-bot', commits: 1287, avatar_url: 'https://github.com/huggingface-bot.png' },
        ],
    }
}

function generateMockActivityData(): ActivityDataPoint[] {
    return Array.from({ length: 30 }, (_, i) => ({
        date: format(subDays(new Date(), 29 - i), 'MMM dd'),
        commits_count: Math.floor(Math.random() * 5000) + 1000,
        additions: Math.floor(Math.random() * 50000) + 10000,
        deletions: Math.floor(Math.random() * 30000) + 5000,
        prs_opened: Math.floor(Math.random() * 200) + 50,
        prs_merged: Math.floor(Math.random() * 150) + 30,
        issues_opened: Math.floor(Math.random() * 100) + 20,
        issues_closed: Math.floor(Math.random() * 80) + 15,
        stars_gained: Math.floor(Math.random() * 500) + 100,
    }))
}

function generateMockLanguageTrends(): LanguageTrend[] {
    const languages = ['Python', 'TypeScript', 'C++', 'Rust', 'Go', 'JavaScript', 'Julia']
    return Array.from({ length: 30 }, (_, i) => {
        const date = format(subDays(new Date(), 29 - i), 'MMM dd')
        return languages.map((lang) => ({
            date,
            language: lang,
            repo_count: Math.floor(Math.random() * 50) + 10,
            total_stars: Math.floor(Math.random() * 10000) + 1000,
        }))
    }).flat()
}

function generateMockTopicTrends() {
    const topics = ['machine-learning', 'deep-learning', 'nlp', 'computer-vision', 'llm', 'transformers']
    return Array.from({ length: 30 }, (_, i) => {
        const date = format(subDays(new Date(), 29 - i), 'MMM dd')
        return topics.map((topic) => ({
            date,
            topic,
            repo_count: Math.floor(Math.random() * 30) + 5,
            total_stars: Math.floor(Math.random() * 5000) + 500,
        }))
    }).flat()
}

// Components
function MetricCard({
    title,
    value,
    change,
    changeLabel,
    icon: Icon,
    iconColor,
}: {
    title: string
    value: string | number
    change?: number
    changeLabel?: string
    icon: React.ComponentType<{ className?: string }>
    iconColor: string
}) {
    const isPositive = change && change > 0
    return (
        <div className="metric-card">
            <div className="flex items-start justify-between">
                <div>
                    <p className="metric-label">{title}</p>
                    <p className="metric-value">{value.toLocaleString()}</p>
                    {change !== undefined && changeLabel && (
                        <div className={clsx('metric-change', isPositive ? 'metric-change-positive' : 'metric-change-negative')}>
                            <TrendingUp className={clsx('h-3 w-3', isPositive ? 'rotate-0' : 'rotate-180')} />
                            <span>{Math.abs(change)}%</span>
                            <span className="text-muted-foreground">{changeLabel}</span>
                        </div>
                    )}
                </div>
                <div className={clsx('p-3 rounded-xl', iconColor)}>
                    <Icon className="h-6 w-6" />
                </div>
            </div>
        </div>
    )
}

function ActivityChart({ data }: { data: ActivityDataPoint[] }) {
    return (
        <div className="bg-card rounded-xl border p-6">
            <h3 className="text-lg font-semibold mb-4">Repository Activity (30 Days)</h3>
            <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                    <ComposedChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis dataKey="date" className="text-xs" tickLine={false} axisLine={false} />
                        <YAxis className="text-xs" tickLine={false} axisLine={false} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px',
                            }}
                            labelStyle={{ color: 'hsl(var(--foreground))' }}
                        />
                        <Legend />
                        <Area
                            type="monotone"
                            dataKey="commits_count"
                            name="Commits"
                            stroke="#0ea5e9"
                            fill="#0ea5e9"
                            fillOpacity={0.1}
                            strokeWidth={2}
                        />
                        <Area
                            type="monotone"
                            dataKey="prs_merged"
                            name="PRs Merged"
                            stroke="#22c55e"
                            fill="#22c55e"
                            fillOpacity={0.1}
                            strokeWidth={2}
                        />
                        <Area
                            type="monotone"
                            dataKey="issues_closed"
                            name="Issues Closed"
                            stroke="#f97316"
                            fill="#f97316"
                            fillOpacity={0.1}
                            strokeWidth={2}
                        />
                        <Bar dataKey="stars_gained" name="Stars" fill="#eab308" radius={[4, 4, 0, 0]} maxBarSize={20} />
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

function LanguageDistributionChart({ data }: { data: Array<{ language: string; count: number }> }) {
    const COLORS = ['#0ea5e9', '#22c55e', '#f97316', '#eab308', '#a855f7', '#ec4899', '#06b6d4', '#84cc16']
    return (
        <div className="bg-card rounded-xl border p-6">
            <h3 className="text-lg font-semibold mb-4">Top Languages</h3>
            <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={100}
                            paddingAngle={2}
                            dataKey="count"
                            nameKey="language"
                            label={({ language, percent }) => `${language} ${(percent * 100).toFixed(0)}%`}
                            labelLine={false}
                        >
                            {data.map((_, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px',
                            }}
                            formatter={(value: number) => [value.toLocaleString(), 'Repositories']}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

function TopicTrendsChart({ data }: { data: Array<{ date: string; topic: string; repo_count: number }> }) {
    const topics = [...new Set(data.map((d) => d.topic))]
    const formattedData = topics.map((topic) => {
        const topicData = data.filter((d) => d.topic === topic)
        return topicData.map((d) => ({ date: d.date, [topic]: d.repo_count }))
    }).flat()

    // Merge by date
    const mergedData = data.reduce((acc, curr) => {
        const existing = acc.find((d) => d.date === curr.date)
        if (existing) {
            existing[curr.topic] = curr.repo_count
        } else {
            acc.push({ date: curr.date, [curr.topic]: curr.repo_count })
        }
        return acc
    }, [] as Array<Record<string, number | string>>)

    return (
        <div className="bg-card rounded-xl border p-6">
            <h3 className="text-lg font-semibold mb-4">AI/ML Topic Trends</h3>
            <div className="chart-container">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={mergedData}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis dataKey="date" className="text-xs" tickLine={false} axisLine={false} />
                        <YAxis className="text-xs" tickLine={false} axisLine={false} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'hsl(var(--card))',
                                border: '1px solid hsl(var(--border))',
                                borderRadius: '8px',
                            }}
                        />
                        <Legend />
                        {topics.map((topic, index) => (
                            <Line
                                key={topic}
                                type="monotone"
                                dataKey={topic}
                                name={topic}
                                stroke={['#0ea5e9', '#22c55e', '#f97316', '#eab308', '#a855f7', '#ec4899'][index % 6]}
                                strokeWidth={2}
                                dot={false}
                                activeDot={{ r: 6 }}
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    )
}

function TopRepositoriesTable({ repositories }: { repositories: Array<{ id: number; full_name: string; stars: number; language: string }> }) {
    return (
        <div className="bg-card rounded-xl border p-6">
            <h3 className="text-lg font-semibold mb-4">Top Repositories by Stars</h3>
            <div className="overflow-x-auto">
                <table className="w-full text-sm">
                    <thead>
                        <tr className="border-b text-left text-muted-foreground">
                            <th className="pb-3 font-medium">Repository</th>
                            <th className="pb-3 font-medium text-right">Stars</th>
                            <th className="pb-3 font-medium text-right">Language</th>
                        </tr>
                    </thead>
                    <tbody>
                        {repositories.map((repo, index) => (
                            <tr key={repo.id} className="border-b last:border-0 hover:bg-accent/50 transition-colors">
                                <td className="py-3 font-medium">
                                    <a href={`https://github.com/${repo.full_name}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:text-primary transition-colors">
                                        {repo.full_name}
                                        <ExternalLink className="h-3 w-3 text-muted-foreground" />
                                    </a>
                                </td>
                                <td className="py-3 text-right text-muted-foreground">{repo.stars.toLocaleString()}</td>
                                <td className="py-3 text-right">
                                    <span className="px-2 py-1 text-xs bg-muted rounded-full">{repo.language}</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    )
}

function TopContributorsTable({ contributors }: { contributors: Array<{ login: string; commits: number; avatar_url: string }> }) {
    return (
        <div className="bg-card rounded-xl border p-6">
            <h3 className="text-lg font-semibold mb-4">Top Contributors</h3>
            <div className="space-y-3">
                {contributors.map((contributor, index) => (
                    <div key={contributor.login} className="flex items-center gap-4 p-3 hover:bg-accent/50 rounded-lg transition-colors">
                        <span className="text-sm text-muted-foreground w-8">#{index + 1}</span>
                        <img src={contributor.avatar_url} alt={contributor.login} className="h-8 w-8 rounded-full" />
                        <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{contributor.login}</p>
                            <p className="text-xs text-muted-foreground">{contributor.commits.toLocaleString()} commits</p>
                        </div>
                        <a href={`https://github.com/${contributor.login}`} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-primary transition-colors">
                            <ExternalLink className="h-4 w-4" />
                        </a>
                    </div>
                ))}
            </div>
        </div>
    )
}

export function DashboardOverview() {
    // In production, these would be real API calls
    const { data: summary } = useQuery({
        queryKey: ['summary'],
        queryFn: async () => generateMockSummaryStats(),
        staleTime: 5 * 60 * 1000,
    })

    const { data: activity } = useQuery({
        queryKey: ['activity'],
        queryFn: async () => generateMockActivityData(),
        staleTime: 5 * 60 * 1000,
    })

    const { data: languageTrends } = useQuery({
        queryKey: ['languageTrends'],
        queryFn: async () => generateMockLanguageTrends(),
        staleTime: 5 * 60 * 1000,
    })

    const { data: topicTrends } = useQuery({
        queryKey: ['topicTrends'],
        queryFn: async () => generateMockTopicTrends(),
        staleTime: 5 * 60 * 1000,
    })

    if (!summary || !activity) {
        return null // Skeleton handled by parent
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Total Repositories"
                    value={summary.total_repositories}
                    change={12.5}
                    changeLabel="vs last month"
                    icon={Database}
                    iconColor="bg-primary/10 text-primary"
                />
                <MetricCard
                    title="AI/ML Repositories"
                    value={summary.total_ai_ml_repositories}
                    change={18.2}
                    changeLabel="vs last month"
                    icon={GitBranch}
                    iconColor="bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400"
                />
                <MetricCard
                    title="Active Contributors"
                    value={summary.total_contributors}
                    change={8.7}
                    changeLabel="vs last month"
                    icon={Users}
                    iconColor="bg-orange-100 text-orange-600 dark:bg-orange-900/30 dark:text-orange-400"
                />
                <MetricCard
                    title="Total Stars"
                    value={summary.total_stars}
                    change={15.3}
                    changeLabel="vs last month"
                    icon={Star}
                    iconColor="bg-yellow-100 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400"
                />
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ActivityChart data={activity} />
                <LanguageDistributionChart data={summary.top_languages} />
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TopicTrendsChart data={topicTrends || []} />
                <div className="bg-card rounded-xl border p-6">
                    <h3 className="text-lg font-semibold mb-4">Commits & Code Changes</h3>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={activity}>
                                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                                <XAxis dataKey="date" className="text-xs" tickLine={false} axisLine={false} />
                                <YAxis yAxisId="left" className="text-xs" tickLine={false} axisLine={false} />
                                <YAxis yAxisId="right" orientation="right" className="text-xs" tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--card))',
                                        border: '1px solid hsl(var(--border))',
                                        borderRadius: '8px',
                                    }}
                                />
                                <Legend />
                                <Bar
                                    yAxisId="left"
                                    dataKey="additions"
                                    name="Additions"
                                    fill="#22c55e"
                                    radius={[4, 4, 0, 0]}
                                    maxBarSize={30}
                                />
                                <Bar
                                    yAxisId="left"
                                    dataKey="deletions"
                                    name="Deletions"
                                    fill="#ef4444"
                                    radius={[4, 4, 0, 0]}
                                    maxBarSize={30}
                                />
                                <Line
                                    yAxisId="right"
                                    type="monotone"
                                    dataKey="commits_count"
                                    name="Commits"
                                    stroke="#0ea5e9"
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Tables Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <TopRepositoriesTable repositories={summary.top_repositories} />
                <TopContributorsTable contributors={summary.top_contributors} />
            </div>
        </div>
    )
}