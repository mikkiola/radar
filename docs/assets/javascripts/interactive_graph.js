document.addEventListener("DOMContentLoaded", function() {
    fetch("/opensource-radar/assets/javascripts/graph.json")
        .then(r => r.json())
        .then(data => {
            var container = document.createElement("div");
            container.id = "graph-container";
            container.style = "width:100%;height:500px;margin:20px 0;border:1px solid #eee;border-radius:4px;";
            var content = document.querySelector("article") || document.querySelector(".md-content__inner");
            if (content) content.prepend(container);
            var chart = echarts.init(container);
            chart.setOption({
                backgroundColor: "#fafafa",
                series: [{
                    type: "graph",
                    layout: "force",
                    data: data.nodes.map(n => ({
                        name: n.name.replace(/_/g, " ").replace(/\s+\d{4}-\d{2}-\d{2}$/, ""),
                        symbolSize: Math.max(n.symbolSize || 3, 3),
                        value: n.value,
                        itemStyle: {color: n.name.includes("Patterns") || n.name.includes("Pattern") ? "#5470c6" : "#91cc75"}
                    })),
                    links: data.links.map(l => ({source: l.source, target: l.target})),
                    roam: true,
                    label: {show: true, fontSize: 9, formatter: p => p.name.length > 20 ? p.name.slice(0,20)+"..." : p.name},
                    force: {repulsion: 300, gravity: 0.05, edgeLength: 80},
                    lineStyle: {color: "#999", width: 1.5, opacity: 0.7},
                    emphasis: {focus: "adjacency"}
                }]
            });
            chart.on("click", function(params) {
                if (params.data && params.data.value) window.location.href = params.data.value;
            });
        });
});
