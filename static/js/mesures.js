var socket = io();

let data;

var timeSlider = document.getElementById("timeSlider");
var timeLabel = document.getElementById("timeLabel");
var pointsLabel = document.getElementById("pointsLabel");
var dateChoice = document.getElementById("dateChoice");
var amplitude = document.getElementById("amplitude");

var date = "";

timeSlider.min = 0;
timeSlider.value = 0;

var nPoint = 200;

socket.on('connect', function () {
  console.log('Connected');
});

socket.on('disconnect', function () {
  console.log('Disconnected');
});

socket.on('metaData', function (data) {
  timeSlider.value = 0;
  timeSlider.max = data.dataLength - nPoint;
  updateData();
});

socket.on('data', function (_data) {
  data = _data;
  if(data.length != 0){
    timeLabel.innerHTML = "heure : " + data[0].timestamp.slice(0,2) + "h " + data[0].timestamp.slice(2,4) + "m " + data[0].timestamp.slice(4,6) + "s ";
    // pointsLabel.innerHTML = "points : " + pointsSlider.value;
    updateChart(data);
  }
});

socket.on('data2', function (data) {
  updateChart2(data);
});

socket.on('amplitude', function (data) {
  amplitude.value = data.amplitude;
});

timeSlider.onchange = function () {
  updateData();
}


nPoint.oninput = function () {
  updateData();
}

function changeDate(element){
  dateChoice.innerHTML = element.innerHTML;
  date = element.innerHTML;
  updateData();
}

function updateData() {
  socket.emit('get_data_position', { index: timeSlider.value, date: date});
}


function responsivefy(svg) {
  const container = d3.select(svg.node().parentNode),
    width = parseInt(svg.style('width'), 10),
    height = parseInt(svg.style('height'), 10),
    aspect = width / height;
  svg.attr('viewBox', `0 0 ${width} ${height}`)
    // .attr('preserveAspectRatio', 'xMinYMid')
    .call(resize);
  d3.select(window).on(
    'resize.' + container.attr('id'),
    resize
  );
  function resize() {
    const w = parseInt(container.style('width'));
    svg.attr('width', w);
    // svg.attr('height', Math.round(w / aspect));
    svg.attr('height', Math.round(window.innerHeight * 0.6));
  }
}

function updateChart(data) {
  var circles = sVg.selectAll("circle")
    .data(data);

  circles.enter()
    .append("circle")
    .merge(circles)
    .attr("cx", function (d) { return x(d.x); })
    .attr("cy", function (d) { return y(d.y); })
    .attr("r", 2)
    .attr("fill", "steelblue");

  circles.exit().remove();
}

function updateChart2(data) {
  var circles = sVg2.selectAll("circle")
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



var margin = { top: 10, right: 10, bottom: 30, left: 40 },
  width = 500 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

var sVg = d3.select("#chartPosition")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var x = d3.scaleLinear()
  .domain([100, 2400])
  .range([0, width]);
sVg
  .append('g')
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));

// X scale and Axis
var y = d3.scaleLinear()
  .domain([100, 2500])
  .range([height, 0]);
sVg
  .append('g')
  .call(d3.axisLeft(y));

sVg.append("text")
  .attr("class", "x label")
  .attr("text-anchor", "end")
  .attr("x", width)
  .attr("y", height - 6)
  .text("axes x mm");

sVg.append("text")
  .attr("class", "y label")
  .attr("text-anchor", "end")
  .attr("y", 6)
  .attr("dy", ".75em")
  .attr("transform", "rotate(-90)")
  .text("axes y mm");

var sVg2 = d3.select("#chartPositionDirect")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

sVg2
  .append('g')
  .attr("transform", "translate(0," + height + ")")
  .call(d3.axisBottom(x));
sVg2
  .append('g')
  .call(d3.axisLeft(y));

sVg2.append("text")
  .attr("class", "x label")
  .attr("text-anchor", "end")
  .attr("x", width)
  .attr("y", height - 6)
  .text("axes x mm");

sVg2.append("text")
  .attr("class", "y label")
  .attr("text-anchor", "end")
  .attr("y", 6)
  .attr("dy", ".75em")
  .attr("transform", "rotate(-90)")
  .text("axes y mm");