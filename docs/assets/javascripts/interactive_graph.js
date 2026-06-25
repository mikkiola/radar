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
                backgroundColor: "#1a1a2e",
                series: [{
                    type: "graph",
                    layout: "force",
                    data: data.nodes.map(n => ({
                        name: n.name.replace(/_/g, " ").replace(/\s+\d{4}-\d{2}-\d{2}$/, ""),
                        symbolSize: Math.max(n.symbolSize || 3, 5),
                        value: n.value,
                        itemStyle: {
                            color: n.name.includes("02_Patterns") || n.value.includes("02_Patterns") ? "#e94560" : "#0f3460",
                            borderColor: "#16213e",
                            borderWidth: 1
                        },
                        label: {color: "#eee"}
                    })),
                    links: data.links.map(l => ({source: l.source, target: l.target})),
                    roam: true,
                    label: {
                        show: true,
                        fontSize: 9,
                        color: "#eee",
                        formatter: p => p.name.length > 25 ? p.name.slice(0,25)+"..." : p.name
                    },
                    force: {repulsion: 400, gravity: 0.05, edgeLength: 100},
                    lineStyle: {color: "#e94560", width: 1, opacity: 0.5},
                    emphasis: {focus: "adjacency"},
                    autoCurveness: true
                }]
            });
            setTimeout(() => chart.resize(), 200);
            chart.on("click", function(params) {
                if (params.data && params.data.value) window.location.href = params.data.value;
            });
        });
});
