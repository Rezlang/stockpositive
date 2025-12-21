import React, { useState } from 'react'
import Highcharts from 'highcharts/highstock'
import HighchartsReact from 'highcharts-react-official'
import { CANDLEDATA } from '../constants/candle-data.const'

type ChartType = 'candlestick' | 'area'

const StockChart: React.FC = () => {
  const [chartType, setChartType] = useState<ChartType>('candlestick')

  // Transform CANDLEDATA for area chart (use close prices)
  const areaData = CANDLEDATA.map(([time, _open, _high, _low, close]) => [time, close])

  // Calculate min/max for y-axis to keep it consistent
  const prices = CANDLEDATA.flatMap(([, open, high, low, close]) => [open, high, low, close])
  const minPrice = Math.min(...prices)
  const maxPrice = Math.max(...prices)

  const commonOptions: Highcharts.Options = {
    chart: { height: 600 },
    rangeSelector: { selected: 1 },
    yAxis: {
      min: minPrice,
      max: maxPrice,
    },
    tooltip: { valueDecimals: 2 },
  }

  const options: Highcharts.Options =
    chartType === 'candlestick'
      ? {
          ...commonOptions,
          title: { text: 'Candlestick Chart' },
          series: [
            {
              type: 'candlestick',
              name: 'Stock Price',
              data: CANDLEDATA,
            },
          ],
        }
      : {
          ...commonOptions,
          title: { text: 'Area Chart' },
          series: [
            {
              type: 'areaspline',
              name: 'Stock Price',
              data: areaData,
              threshold: null,
              color: '#2caffe',
              fillColor: {
                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                stops: [
                  [0, '#2caffe'],
                  [1, '#2caffe00'],
                ],
              },
            },
          ],
        }

  // Button styles (reverse colors: selected = colored bg, deselected = white)
  const getButtonStyle = (type: ChartType) =>
    chartType === type
      ? { backgroundColor: '#2caffe', color: '#fff', border: '1px solid #2caffe', cursor: 'default' }
      : { backgroundColor: '#fff', color: '#2caffe', border: '1px solid #2caffe', cursor: 'pointer' }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '20px' }}>
        <button onClick={() => setChartType('candlestick')} style={getButtonStyle('candlestick')}>
          Candlestick
        </button>
        <button onClick={() => setChartType('area')} style={{ ...getButtonStyle('area'), marginLeft: '10px' }}>
          Area
        </button>
      </div>
      <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto', boxSizing: 'border-box' }}>
        <HighchartsReact highcharts={Highcharts} constructorType="stockChart" options={options} />
      </div>
    </div>
  )
}

export default StockChart
