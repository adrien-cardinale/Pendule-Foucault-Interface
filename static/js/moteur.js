var socket = io();

let data;
let time;

var timeSlider = document.getElementById("timeSlider");
var timeLabel = document.getElementById("timeLabel");
var dateChoice = document.getElementById("dateChoice");
var minCurrent = document.getElementById("minCurrent");
var maxCurrent = document.getElementById("maxCurrent");
var spinner = document.getElementById("spinner");

var margin = { top: 10, right: 80, bottom: 60, left: 60 },
  width = 800 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

var date = "";

var colorI = 'steelblue'
var colorP = 'orange'

var numericP;
var numericI;

timeSlider.min = 0;
timeSlider.value = 0;

var nPoint = 200;

socket.on('connect', function () {
    console.log('Connected');
});

socket.on('disconnect', function () {
  spinner.style.visibility = "visible";
  console.log('Disconnected');
});

socket.on('metaData_moteur', function (data) {
  
  console.log(data);
  timeSlider.value = 0;
  timeSlider.max = data.dataLength - nPoint;
  updateData();
});

socket.on('data_moteur', function (_data) {
  spinner.style.visibility = "hidden";
  data = _data;
  console.log("data length : " + data.length);
  numericP = data.map(item => parseFloat(item.p));
  numericI = data.map(item => parseFloat(item.I));
  minCurrent.value = Math.min(...numericI).toFixed(2);
  maxCurrent.value = Math.max(...numericI).toFixed(2);
  if(data.length != 0){
    timeLabel.innerHTML = "heure : " + data[0].timestamp.slice(0,2) + "h " + data[0].timestamp.slice(2,4) + "m " + data[0].timestamp.slice(4,6) + "s à " + data[data.length - 1].timestamp.slice(0,2) + "h " + data[data.length - 1].timestamp.slice(2,4) + "m " + data[data.length - 1].timestamp.slice(4,6) + "s ";
    updateChart(data);
  }
});

timeSlider.onchange = function () {
  updateData();
}

function changeDate(element){
  spinner.style.visibility = "visible";
  socket.emit('change_date_moteur', element.innerHTML);
  dateChoice.innerHTML = element.innerHTML;
  date = element.innerHTML;
  updateData();
}

function updateData() {
  socket.emit('get_data_moteur', { index: timeSlider.value, date: date });
}


function responsivefy(svg) {
    const container = d3.select(svg.node().parentNode),
      width = parseInt(svg.style('width'), 10),
      height = parseInt(svg.style('height'), 10),
      aspect = width / height;
    svg.attr('viewBox', `0 0 ${width} ${height}`)
      .call(resize);
    d3.select(window).on(
      'resize.' + container.attr('id'),
      resize
    );
    function resize() {
      const w = parseInt(container.style('width'));
      svg.attr('width', w);
      svg.attr('height', Math.round(window.innerHeight * 0.6));
    }
}

var formatTime = d3.timeFormat("%S");    

function updateChart(data) {

    sVg.selectAll("*").remove();
    data.forEach(function(d) {
      var hour = +d.timestamp.slice(0,2);
      var minute = +d.timestamp.slice(2,4);
      var second = +d.timestamp.slice(4,6);
      var millisecond = +d.timestamp.slice(6,9);
      d.timestamp = new Date(1970, 0, 1, hour, minute, second, millisecond);
    });

    var x = d3.scaleTime() 
    .domain(d3.extent(data, function(d) { return d.timestamp; }))
    .range([0, width]);

  sVg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(x).tickFormat(formatTime));

    var yI = d3.scaleLinear()
      .domain([Math.min(...numericI), Math.max(...numericI)])
      .range([height, 0]);
    sVg
      .append('g')
      .call(d3.axisLeft(yI));

    var yP = d3.scaleLinear()
      .domain([Math.min(...numericP), Math.max(...numericP)])
      .range([height, 0]);

    sVg
      .append('g')
      .attr("transform", "translate(" + width + ",0)")
      .call(d3.axisRight(yP));

    const lineI = d3.line()
        .x(function (d) { return x(d.timestamp); })
        .y(function (d) { return yI(d.I); });

    sVg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", colorI)
        .attr("stroke-width", 1.5)
        .attr("d", lineI);

    const lineP = d3.line()
        .x(function (d) { return x(d.timestamp); })
        .y(function (d) { return yP(d.p); });
    
    sVg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", colorP)
        .attr("stroke-width", 1.5)
        .attr("d", lineP);

    sVg.append("text")
        .attr("transform", "translate(" + (width / 2) + " ," + (height + 40) + ")")
        .style("text-anchor", "middle")
        .text("Temps [s]");

    sVg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", -margin.left)
        .attr("x", -(height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Courant dans le moteur [A]")
        .attr("fill", colorI);

    sVg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", width+margin.right/2)
        .attr("x", -(height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Position du moteur [m]")
        .attr("fill", colorP);
}



var sVg = d3.select("#chartDriver")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");