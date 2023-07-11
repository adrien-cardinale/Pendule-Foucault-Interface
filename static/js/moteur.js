var socket = io();

let data;

var timeSlider = document.getElementById("timeSlider");
var timeLabel = document.getElementById("timeLabel");
var dateChoice = document.getElementById("dateChoice");

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
  timeSlider.max = data.dataLength - 1;
  socket.emit('get_data_moteur', { time: timeSlider.value, points: nPoint });
});

socket.on('data_moteur', function (_data) {
  data = _data;
  console.log(data)
  if(data.length != 0){
    timeLabel.innerHTML = "heure : " + data[0].timestamp.slice(0,2) + "h " + data[0].timestamp.slice(2,4) + "m " + data[0].timestamp.slice(4,6) + "s ";
    // pointsLabel.innerHTML = "points : " + pointsSlider.value;
    updateChart(data);
  }
});

timeSlider.oninput = function () {
  updateData();
}

function changeDate(element){
  dateChoice.innerHTML = element.innerHTML;
  socket.emit('change_date', { date: element.innerHTML });
}

function updateData() {
  console.log(timeSlider.value);
  socket.emit('get_data_moteur', { time: timeSlider.value, points: nPoint });
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
    console.log(data);
    sVg.selectAll("*").remove();

    var x = d3.scaleLinear()
      //domain with min and max of data
      .domain([d3.min(data, function (d) { return d.timestamp; }), d3.max(data, function (d) { return d.timestamp; })])
      .range([0, width]);
    sVg
      .append('g')
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    // X scale and Axis
    var y = d3.scaleLinear()
      .domain([-10, 10])
      .range([height, 0]);
    sVg
      .append('g')
      .call(d3.axisLeft(y));
    
    const line = d3.line()
        .x(function (d) { return x(d.timestamp); })
        .y(function (d) { return y(d.I); });

    sVg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", line);
}

var margin = { top: 10, right: 10, bottom: 30, left: 40 },
  width = 500 - margin.left - margin.right,
  height = 400 - margin.top - margin.bottom;

var sVg = d3.select("#chartDriver")
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .call(responsivefy)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



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