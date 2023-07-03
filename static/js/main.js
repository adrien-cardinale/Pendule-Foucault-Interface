var socket = io();

var data = [];

socket.on('connect', function () {
  console.log('Connected');
});

socket.on('data', function (_data) {
  data = _data;
  updateChart(data);
});

function responsivefy(svg) {
  const container = d3.select(svg.node().parentNode),
    width = parseInt(svg.style('width'), 10),
    height = parseInt(svg.style('height'), 10),
    aspect = width / height;
  svg.attr('viewBox', `0 0 ${width} ${height}`)
    .attr('preserveAspectRatio', 'xMinYMid')
    .call(resize);
  d3.select(window).on(
    'resize.' + container.attr('id'),
    resize
  );
  function resize() {
    const w = parseInt(container.style('width'));
    svg.attr('width', w);
    svg.attr('height', Math.round(w / aspect));
  }
}

var margin = { top: 10, right: 10, bottom: 30, left: 40 },
  width = 500 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

var sVg = d3.select("#chart")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var x = d3.scaleLinear()
  .domain([1500, -1500])
  .range([0, width]);
sVg
  .append('g')
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));

// X scale and Axis
var y = d3.scaleLinear()
  .domain([1500, -1500])
  .range([height, 0]);
sVg
  .append('g')
  .call(d3.axisLeft(y));

function updateChart(data) {
  var circles = sVg.selectAll("circle")
    .data(data);

  circles.enter()
    .append("circle")
    .merge(circles)
    .attr("cx", function (d) { return x(d.x); })
    .attr("cy", function (d) { return y(d.y); })
    .attr("r", 5)
    .attr("fill", "steelblue");

  circles.exit().remove();

}