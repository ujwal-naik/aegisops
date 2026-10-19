import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_architecture():
    # Set high DPI figure with widescreen aspect ratio
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=300)
    fig.patch.set_facecolor('#0B132B')  # Dark tactical slate/navy background
    ax.set_facecolor('#0B132B')
    
    # Hide axes
    ax.axis('off')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 45)
    
    # Define box styles
    layer_configs = [
        {
            "name": "1. FIELD & INGESTION",
            "box": (2, 8, 21, 30),
            "color": "#1C2541",
            "edge": "#48E5C2",
            "items": ["• Offline PWA Client", "• Service Worker Cache", "• IndexedDB Vault", "• SOS Report Logger", "• Multi-Lingual Input"]
        },
        {
            "name": "2. DTN MESH SYNC",
            "box": (26.5, 8, 21, 30),
            "color": "#1C2541",
            "edge": "#5BC0BE",
            "items": ["• Store & Forward Mesh", "• P2P Bundle Exchange", "• Zero Cellular Needed", "• Cryptographic Bundles", "• Auto-Reconciliation"]
        },
        {
            "name": "3. NLP & SPATIAL CORE",
            "box": (51, 8, 22, 30),
            "color": "#1C2541",
            "edge": "#F26419",
            "items": ["• START Clinical Triage", "  (Red/Yellow/Green/Black)", "• Haversine Cluster (500m)", "• Jaccard Deduplication", "• Trauma Priority Scoring"]
        },
        {
            "name": "4. ICS-204 & GIS",
            "box": (76.5, 8, 21.5, 30),
            "color": "#1C2541",
            "edge": "#E71D36",
            "items": ["• Capability Matching", "  (Boats, Medics, SAR)", "• Anti-Starvation Fairness", "• Tactical Dark Leaflet Map", "• Human Override Control"]
        }
    ]
    
    # Draw layers
    for cfg in layer_configs:
        x, y, w, h = cfg["box"]
        # Rounded rectangle
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.8,rounding_size=1.2",
                                      facecolor=cfg["color"], edgecolor=cfg["edge"], linewidth=2.2, zorder=2)
        ax.add_patch(rect)
        
        # Layer Header
        ax.text(x + w/2, y + h - 3, cfg["name"], ha='center', va='center',
                fontsize=8.5, fontweight='bold', color=cfg["edge"], fontfamily='sans-serif', zorder=3)
        
        # Sub-header separator line
        ax.plot([x + 1, x + w - 1], [y + h - 5.5, y + h - 5.5], color=cfg["edge"], linewidth=0.8, alpha=0.5, zorder=3)
        
        # Items
        cur_y = y + h - 8.5
        for item in cfg["items"]:
            indent = 1.0 if not item.startswith("  ") else 2.2
            color = "#FFFFFF" if not item.startswith("  ") else "#A3CEF1"
            weight = 'normal'
            size = 7.2 if not item.startswith("  ") else 6.8
            ax.text(x + indent, cur_y, item, ha='left', va='center',
                    fontsize=size, fontweight=weight, color=color, fontfamily='sans-serif', zorder=3)
            cur_y -= 4.2

    # Draw connection arrows between layers
    arrow_props = dict(facecolor='#48E5C2', edgecolor='#48E5C2', arrowstyle="simple,tail_width=2.0,head_width=5.0,head_length=5.0", lw=1)
    
    # Arrow 1 -> 2
    ax.annotate('', xy=(25.8, 23), xytext=(23.7, 23), arrowprops=arrow_props, zorder=5)
    # Arrow 2 -> 3
    arrow_props["facecolor"] = '#5BC0BE'
    arrow_props["edgecolor"] = '#5BC0BE'
    ax.annotate('', xy=(50.3, 23), xytext=(48.2, 23), arrowprops=arrow_props, zorder=5)
    # Arrow 3 -> 4
    arrow_props["facecolor"] = '#F26419'
    arrow_props["edgecolor"] = '#F26419'
    ax.annotate('', xy=(75.8, 23), xytext=(73.7, 23), arrowprops=arrow_props, zorder=5)

    # Title label at top
    ax.text(50, 42.5, "AEGISOPS END-TO-END PIPELINE ARCHITECTURE", ha='center', va='center',
            fontsize=12, fontweight='bold', color='#FFFFFF', fontfamily='sans-serif')

    plt.tight_layout()
    plt.savefig('docs/screenshots/architecture_diagram.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print("Architecture diagram generated successfully at docs/screenshots/architecture_diagram.png")

if __name__ == '__main__':
    generate_architecture()
