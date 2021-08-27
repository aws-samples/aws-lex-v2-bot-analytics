// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0
const d3 = require('d3'); // eslint-disable-line import/no-unresolved
const jsdom = require('jsdom'); // eslint-disable-line import/no-unresolved

const { JSDOM } = jsdom;

// eslint-disable-next-line object-curly-newline
function displayHeatMap({ data, widgetContext, groups, vars } = {}) {
  // create a new JSDOM instance for d3-selection to use
  const { document } = new JSDOM().window;

  // set the dimensions and margins of the graph
  const margin = {
    top: 30,
    right: 30,
    bottom: 120,
    left: 30,
  };
  const width = widgetContext.width - margin.left - margin.right;
  const height = widgetContext.height - margin.top - margin.bottom;

  // append the svg object to the body of the page
  const svg = d3
    .select(document.body)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left}, ${margin.top})`);

  // Labels of row and columns

  // Build X scales and axis:
  const scaleX = d3.scaleBand().range([0, width]).domain(groups).padding(0.005);
  svg
    .append('g')
    .classed('axis-x', true)
    .attr('transform', `translate(0, ${height})`)
    .call(d3.axisBottom(scaleX))
    .selectAll('text')
    .style('text-anchor', 'end')
    .attr('dx', '-.8em')
    .attr('dy', '.15em')
    .attr('transform', 'rotate(-65)');

  // Build Y scales and axis:
  const scaleY = d3.scaleBand().range([height, 0]).domain(vars).padding(0.01);
  svg.append('g').classed('axis-y', true).call(d3.axisLeft(scaleY));

  // Build color scale
  const values = data.map((d) => d.value);
  const setColorScalar = d3
    .scaleLinear()
    .range(['#fff', '#A3320B'])
    .domain([d3.min(values), d3.max(values)]);

  const dataGroup = svg
    .selectAll()
    .data(data, (d) => `${d.group}:${d.variable}`)
    .enter()
    .append('g')
    .classed('datagroup', true);

  dataGroup
    .append('rect')
    .attr('x', (d) => scaleX(d.group))
    .attr('y', (d) => scaleY(d.variable))
    .attr('width', scaleX.bandwidth())
    .attr('height', scaleY.bandwidth())
    .style('fill', (d) => setColorScalar(d.value));

  dataGroup
    .append('text')
    .text((d) => d.value)
    .attr('x', (d) => scaleX(d.group) + 14)
    .attr('y', (d) => scaleY(d.variable) + 14)
    .classed('text-value', true);
  const CSS = `
    <style>
    .datagroup .text-value { visibility: hidden;}
    .datagroup:hover .text-value { visibility: visible;}
    </style>
  `;

  return CSS + document.body.innerHTML;
}

function displayHeatmapSessionHourOfDay({ widgetContext, queryResults }) {
  const {
    timeRange: { start, end },
  } = widgetContext;
  // at least four hours
  if ((end - start) / 1000 / 60 / 60 < 4) {
    return '<pre class="error">Time range should be greater than 4 hours</pre>';
  }
  const data = queryResults
    .map((x) => x.reduce((a, c) => ({ [c.field]: c.value, ...a }), {}))
    .map((x) => {
      const d = new Date(x['@t']);
      return {
        // TODO handle locales
        group: d.toLocaleString('en-US', { weekday: 'short' }),
        variable: `0${d.getHours()}`.slice(-2),
        value: Number(x['@count']),
      };
    });

  // TODO locale
  const groups = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const vars = ['00', '02', '04', '06', '08', '10', '12', '14', '16', '18', '20', '22'];

  return displayHeatMap({
    data,
    widgetContext,
    groups,
    vars,
  });
}

function displayHeatmapIntentPerHour({ widgetContext, queryResults }) {
  const data = queryResults
    .map((x) => x.reduce((a, c) => ({ [c.field]: c.value, ...a }), {}))
    .map((x) => {
      const d = new Date(x['@t']);
      return {
        group: x['@intent'],
        variable: `0${d.getHours()}`.slice(-2),
        value: Number(x['@count']),
      };
    });

  const groups = Array.from(new Set(data.map((x) => x.group))).sort();
  const vars = Array.from(new Set(data.map((x) => x.variable))).sort();

  return displayHeatMap({
    data,
    widgetContext,
    groups,
    vars,
  });
}

module.exports = {
  displayHeatmapSessionHourOfDay,
  displayHeatmapIntentPerHour,
};
