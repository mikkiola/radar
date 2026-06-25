document.addEventListener("DOMContentLoaded", function() {
    fetch("/assets/javascripts/graph.json")
        .then(r => r.json())
        .then(data => {
            var container = document.createElement("div");
            container.id = "graph-container";
            container.style = "width:100%;height:400px;margin:20px 0;";
            var content = document.querySelector("article") || document.querySelector(".md-content");
            if (content) content.prepend(container);
            var chart = echarts.init(container);
            chart.setOption({
                series: [{
                    type: "graph",
                    layout: "force",
                    data: data.nodes.map(n => ({name: n.name, symbolSize: n.symbolSize || 5, value: n.value})),
                    links: data.links,
                    roam: true,
                    label: {show: true, fontSize: 10},
                    force: {repulsion: 200},
                    lineStyle: {color: "#aaa", width: 1}
                }]
            });
            chart.on("click", function(params) {
                if (params.data.value) window.location.href = params.data.value;
            });
        });
});
