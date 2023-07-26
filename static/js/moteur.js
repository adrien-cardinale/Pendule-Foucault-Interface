var socket = io();

let data;
let time;

var timeSlider = document.getElementById("timeSlider");
var timeLabel = document.getElementById("timeLabel");
var dateChoice = document.getElementById("dateChoice");

var colorI = 'steelblue'
var colorP = 'orange'

timeSlider.min = 0;
timeSlider.value = 0;

var nPoint = 200;

socket.on('connect', function () {
    console.log('Connected');
});

socket.on('disconnect', function () {
  console.log('Disconnected');
});

socket.on('metaData_moteur', function (data) {
  console.log(data);
  timeSlider.value = 0;
  timeSlider.max = data.dataLength - nPoint;
  socket.emit('get_data_moteur', { time: timeSlider.value, points: nPoint });
});

socket.on('data_moteur', function (_data) {
  data = _data;
  console.log("data length : " + data.length);
  if(data.length != 0){
    timeLabel.innerHTML = "heure : " + data[0].timestamp.slice(0,2) + "h " + data[0].timestamp.slice(2,4) + "m " + data[0].timestamp.slice(4,6) + "s ";
    updateChart(data);
  }
});

timeSlider.onchange = function () {
  updateData();
}

function changeDate(element){
  dateChoice.innerHTML = element.innerHTML;
  socket.emit('change_date_moteur', { date: element.innerHTML });
}

function updateData() {
  socket.emit('get_data_moteur', { time: timeSlider.value, points: nPoint });
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

    

function updateChart(data) {
    sVg.selectAll("*").remove();

    var x = d3.scaleLinear()
      .domain([data[0].timestamp, data[data.length - 1].timestamp])
      .range([0, width]);
    sVg
      .append('g')
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    var yI = d3.scaleLinear()
      .domain([-10, 10])
      .range([height, 0]);
    sVg
      .append('g')
      .call(d3.axisLeft(yI));

    var yP = d3.scaleLinear()
      .domain([-0.015, 0.015])
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
        .text("Temps");

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
        .attr("y", width + margin.right)
        .attr("x", -(height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Position du moteur [m]")
        .attr("fill", colorP);
}

var margin = { top: 10, right: 60, bottom: 60, left: 40 },
  width = 800 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

var sVg = d3.select("#chartDriver")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");