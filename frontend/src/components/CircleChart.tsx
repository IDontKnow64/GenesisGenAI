"use client"

import * as React from "react"
import { TrendingUp } from "lucide-react"
import { Label, Pie, PieChart } from "recharts"
import { useState } from "react"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartConfig,
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import { Button } from "./ui/button"


const chartConfig = {
  visitors: {
    label: "Score",
  },
  level: {
    label: "safety",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig

const CircleChart = ({msg_id, description, type, reasons,score}) => {
  const chartData = [
    { level: "safety", score: score, fill: "green" },
    { level: "danger", score: 100-score, fill: "red" },
    { level: "unknown", score: 0, fill: "gray" },
  ]

  return (
    <Card className="flex flex-col">
      <CardHeader className="items-center pb-0">
        <CardTitle>Safety Level</CardTitle>
        <CardDescription>Risk + Summary</CardDescription>
      </CardHeader>
      <CardContent className="flex-1 pb-0 -mt-20">
        <ChartContainer
          config={chartConfig}
          className="mx-auto aspect-square max-h-[250px]"
        >
          <PieChart className="">
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Pie
              data={chartData}
              dataKey="score"
              nameKey="level"
              innerRadius={60}
              strokeWidth={5}
            >
              <Label
                content={({ viewBox }) => {
                  if (viewBox && "cx" in viewBox && "cy" in viewBox) {
                    return (
                      <text
                        x={viewBox.cx}
                        y={viewBox.cy}
                        textAnchor="middle"
                        dominantBaseline="middle"
                      >
                        <tspan
                          x={viewBox.cx}
                          y={viewBox.cy}
                          className="fill-foreground text-3xl font-bold"
                        >
                          {score.toLocaleString()}
                        </tspan>
                        <tspan
                          x={viewBox.cx}
                          y={(viewBox.cy || 0) + 24}
                          className="fill-muted-foreground"
                        >
                          Safety Score
                        </tspan>
                      </text>
                    )
                  }
                }}
              />
            </Pie>
          </PieChart>
        </ChartContainer>
      </CardContent>
      <CardFooter className="-mt-6 flex-col gap-2 text-sm">
        <div className="text-center leading-none text-muted-foreground">
          {description}
        </div>
      </CardFooter>
    </Card>
  )
}

export default CircleChart;