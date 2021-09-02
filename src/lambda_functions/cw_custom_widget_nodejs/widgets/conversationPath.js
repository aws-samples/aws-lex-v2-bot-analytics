// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: MIT-0

// This module is a prototype of conversation path
// TODO add a lengend to reflect link color direction black => forward), red => circular
const d3 = require('d3'); // eslint-disable-line import/no-unresolved
const { sankeyCircular: d3SankeyCircular, sankeyJustify } = require('d3-sankey-circular'); // eslint-disable-line import/no-unresolved
const jsdom = require('jsdom'); // eslint-disable-line import/no-unresolved

const { JSDOM } = jsdom;

const START_NODE_NAME = 'START';

function displaySankey({ data, widgetContext } = {}) {
  // based on:
  // https://bl.ocks.org/tomshanley/6f3fcf68c0dbc401548733dd0c64e3c3
  const { document } = new JSDOM().window;

  // set the dimensions and margins
  const margin = {
    top: 20,
    right: 20,
    bottom: 20,
    left: 20,
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

  const sankey = d3SankeyCircular()
    .nodeId((d) => d.name)
    .nodeWidth(30)
    .nodePaddingRatio(0.8)
    .nodeAlign(sankeyJustify)
    .circularLinkGap(20)
    .extent([
      [5, 5],
      [width - 5, height - 5],
    ]);

  const { nodes, links } = sankey(data);

  const color = d3.scaleSequential(d3.interpolateCool).domain([0, width]);

  function getTitle(d) {
    const totalValue = d3.sum(
      nodes.filter((node) => node.name !== START_NODE_NAME),
      (i) => i.value // eslint-disable-line comma-dangle
    );
    const nodePercent = d3.format('.0%')(d.value / totalValue);
    if (d.name === START_NODE_NAME) {
      return `${d.name}`;
    }
    return `${d.name}\n${d.value} (${nodePercent})`;
  }

  svg
    .append('g')
    .selectAll('rect')
    .data(nodes)
    .join('rect')
    .attr('x', (d) => d.x0)
    .attr('y', (d) => d.y0)
    .attr('height', (d) => Math.max(20, d.y1 - d.y0))
    .attr('width', (d) => Math.max(20, d.x1 - d.x0))
    .style('fill', (d) => color(d.x0))
    .style('opacity', 0.5)
    .append('title')
    .text((d) => getTitle(d));

  svg
    .append('g')
    .attr('font-family', 'sans-serif')
    .attr('font-size', 14)
    .attr('fill', '#202630')
    .selectAll('text')
    .data(nodes)
    .join('text')
    .attr('x', (d) => (d.x0 < width / 2 ? d.x0 : d.x1))
    .attr('y', (d) => (d.y1 < width / 2 ? d.y1 + 12 : d.y0 - 12))
    .attr('dy', '0.35em')
    .attr('text-anchor', (d) => (d.x0 < width / 2 ? 'start' : 'end'))
    .text((d) => `${d.name}`)
    .append('title')
    .text((d) => getTitle(d));

  svg
    .append('defs')
    .append('marker')
    .attr('id', 'arrow')
    .attr('viewBox', [0, -5, 10, 10])
    .attr('refX', 8)
    .attr('refY', 0)
    .attr('markerWidth', 2)
    .attr('markerHeight', 2)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M0,-5L10,0L0,5')
    .attr('fill-opacity', 0.05)
    .attr('stroke-opacity', 0.65)
    .attr('stroke', 'black');

  svg
    .append('g')
    .attr('class', 'links')
    .attr('fill', 'none')
    .attr('stroke-opacity', 0.2)
    .selectAll('path')
    .data(links)
    .enter()
    .append('path')
    .attr('d', (d) => d.path)
    .attr('marker-end', 'url(#arrow)')
    .style('stroke-width', (d) => Math.max(4, d.width / 10))
    .style('stroke', (link) => (link.circular ? 'red' : 'black'))
    .append('title')
    .text((d) => `${d.source.name} → ${d.target.name}`);

  return document.body.innerHTML;
}

function displayConversationPath({ widgetContext, queryResults }) {
  // flatten CloudWatch Insights results into objects
  const results = queryResults.map((x) => x.reduce((a, c) => ({ [c.field]: c.value, ...a }), {}));
  if (!results?.length) {
    return '<pre class="error">No data found</pre>';
  }
  const nodes = [
    ...new Set(results.map((x) => x['@intentName'])),
    // add artificial start intent to have a single entry point
    START_NODE_NAME,
  ].map((i) => ({ name: i, category: i }));

  // group results by session id
  const resultsBySessionId = results.reduce((a, e) => {
    const sessionId = e['@sessionId'];
    const entries = a[sessionId] || [];
    return {
      ...a,
      ...{ [sessionId]: [...entries, e] },
    };
  }, {});

  const intentsPerSessionId = Object.keys(resultsBySessionId)
    // add a 'START' intent to each session to introduce a common initial point
    .map((i) => [{ '@intentName': START_NODE_NAME }, ...resultsBySessionId[i]]);

  // rollup sum of unique paths
  const linksRollup = intentsPerSessionId
    .map(
      // create pairs of intents to build source and destination links
      (result) =>
        result // eslint-disable-line implicit-arrow-linebreak
          .map((_, index, array) => array.slice(index, index + 2))
          // remove same source and destination to avoid circular links
          .filter((i) => i.length === 2 && i[0]['@intentName'] !== i[1]['@intentName'])
          // map to objects with source and destination attributes
          .map((i) => ({ source: i[0]['@intentName'], target: i[1]['@intentName'], count: 1 })) // eslint-disable-line comma-dangle
    )
    // flatten into a single array
    .reduce((a, e) => [...a, ...e], [])
    // create an object with aggregated sums of times a source and destination
    // pair path has been traveled
    .reduce((a, e) => {
      const key = `${e.source}:${e.target}`;
      return { ...a, ...{ [key]: a[key] ? a[key] + 1 : 1 } };
    }, {});

  const links = Object.keys(linksRollup).map((e) => {
    const [source, target] = e.split(':');
    return { source, target, value: linksRollup[e] };
  });

  const data = { nodes, links, units: 'count' };
  return displaySankey({ data, widgetContext });
}

module.exports = {
  displayConversationPath,
};
