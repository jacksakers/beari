"""
Database HTML Export Tool for Beari AI
Generates an interactive HTML file to view database contents in a browser.
"""

import sys
from db.db_helpers import DatabaseHelper
from datetime import datetime


def generate_html(db, output_file="beari_database.html"):
    """
    Generate an HTML file with all database contents in a readable format.
    
    Args:
        db: DatabaseHelper instance with active connection
        output_file: Path to the output HTML file
    """
    # Fetch all data
    stats = db.get_stats()
    all_words = db.get_all_words()
    
    # Get all relations
    db.cursor.execute("""
        SELECT va.word as word_a, r.relation_type, vb.word as word_b, r.weight, r.created_at
        FROM relations r
        JOIN vocabulary va ON r.word_a_id = va.id
        JOIN vocabulary vb ON r.word_b_id = vb.id
        ORDER BY r.relation_type, va.word
    """)
    all_relations = [dict(row) for row in db.cursor.fetchall()]
    
    # Group words by POS
    words_by_pos = {}
    words_by_meaning = {}
    for word in all_words:
        pos = word['pos_tag'] or 'Unknown'
        if pos not in words_by_pos:
            words_by_pos[pos] = []
        words_by_pos[pos].append(word)
        
        if word['meaning_tag']:
            meaning = word['meaning_tag']
            if meaning not in words_by_meaning:
                words_by_meaning[meaning] = []
            words_by_meaning[meaning].append(word)
    
    # Group relations by type
    relations_by_type = {}
    for rel in all_relations:
        rel_type = rel['relation_type']
        if rel_type not in relations_by_type:
            relations_by_type[rel_type] = []
        relations_by_type[rel_type].append(rel)
    
    # Generate HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beari AI Database Viewer</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .tabs {{
            display: flex;
            background: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
            padding: 0 40px;
        }}
        
        .tab {{
            padding: 15px 30px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 1em;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
        }}
        
        .tab:hover {{
            color: #667eea;
            background: rgba(102, 126, 234, 0.05);
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            background: white;
        }}
        
        .tab-content {{
            display: none;
            padding: 40px;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            font-size: 1.8em;
            color: #212529;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .section h3 {{
            font-size: 1.3em;
            color: #495057;
            margin: 25px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #667eea;
        }}
        
        .word-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .word-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            transition: all 0.3s;
        }}
        
        .word-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transform: translateY(-2px);
        }}
        
        .word-card .word {{
            font-size: 1.2em;
            font-weight: bold;
            color: #212529;
            margin-bottom: 8px;
        }}
        
        .word-card .tags {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .tag {{
            display: inline-block;
            padding: 4px 10px;
            background: #e9ecef;
            border-radius: 12px;
            font-size: 0.75em;
            color: #495057;
            font-weight: 600;
        }}
        
        .tag.pos {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .tag.meaning {{
            background: #d4edda;
            color: #155724;
        }}
        
        .tag.plural {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .relations-list {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .relation-item {{
            padding: 12px;
            background: white;
            margin-bottom: 10px;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .relation-item .word-a {{
            font-weight: bold;
            color: #667eea;
            min-width: 120px;
        }}
        
        .relation-item .arrow {{
            color: #6c757d;
        }}
        
        .relation-item .rel-type {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
            min-width: 100px;
            text-align: center;
        }}
        
        .relation-item .word-b {{
            font-weight: bold;
            color: #764ba2;
        }}
        
        .relation-item .weight {{
            margin-left: auto;
            background: #f8d7da;
            color: #721c24;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        
        .search-box {{
            margin-bottom: 25px;
            position: sticky;
            top: 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            z-index: 100;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 12px 20px;
            font-size: 1em;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            transition: border-color 0.3s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        
        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }}
        
        .empty-state-icon {{
            font-size: 4em;
            margin-bottom: 20px;
            opacity: 0.3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐻 Beari AI Database</h1>
            <p class="subtitle">Interactive Database Viewer</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{stats['vocabulary_size']}</div>
                <div class="label">Total Words</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['total_relations']}</div>
                <div class="label">Relations</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['relation_types']}</div>
                <div class="label">Relation Types</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(words_by_pos)}</div>
                <div class="label">POS Categories</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('vocabulary')">📚 Vocabulary</button>
            <button class="tab" onclick="showTab('relations')">🔗 Relations</button>
            <button class="tab" onclick="showTab('by-meaning')">🏷️ By Meaning</button>
        </div>
        
        <div id="vocabulary" class="tab-content active">
            <div class="search-box">
                <input type="text" id="vocabSearch" placeholder="🔍 Search vocabulary..." onkeyup="filterVocabulary()">
            </div>
            
            <div class="section" id="vocabularyContent">
"""
    
    # Add vocabulary grouped by POS
    if words_by_pos:
        for pos in sorted(words_by_pos.keys()):
            word_list = words_by_pos[pos]
            html_content += f"""
                <h3>{pos} ({len(word_list)})</h3>
                <div class="word-grid">
"""
            for word in sorted(word_list, key=lambda x: x['word']):
                tags_html = f'<span class="tag pos">{word["pos_tag"]}</span>' if word['pos_tag'] else ''
                if word['meaning_tag']:
                    tags_html += f'<span class="tag meaning">{word["meaning_tag"]}</span>'
                if word['is_plural']:
                    tags_html += '<span class="tag plural">plural</span>'
                
                html_content += f"""
                    <div class="word-card">
                        <div class="word">{word['word']}</div>
                        <div class="tags">{tags_html}</div>
                    </div>
"""
            html_content += """
                </div>
"""
    else:
        html_content += """
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <p>No vocabulary words found in the database.</p>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div id="relations" class="tab-content">
            <div class="search-box">
                <input type="text" id="relSearch" placeholder="🔍 Search relations..." onkeyup="filterRelations()">
            </div>
            
            <div class="section" id="relationsContent">
"""
    
    # Add relations grouped by type
    if relations_by_type:
        for rel_type in sorted(relations_by_type.keys()):
            rel_list = relations_by_type[rel_type]
            html_content += f"""
                <h3>{rel_type.replace('_', ' ').title()} ({len(rel_list)})</h3>
                <div class="relations-list">
"""
            for rel in sorted(rel_list, key=lambda x: x['word_a']):
                weight_html = f'<span class="weight">×{rel["weight"]}</span>' if rel['weight'] > 1 else ''
                html_content += f"""
                    <div class="relation-item">
                        <span class="word-a">{rel['word_a']}</span>
                        <span class="arrow">→</span>
                        <span class="rel-type">{rel['relation_type']}</span>
                        <span class="arrow">→</span>
                        <span class="word-b">{rel['word_b']}</span>
                        {weight_html}
                    </div>
"""
            html_content += """
                </div>
"""
    else:
        html_content += """
                <div class="empty-state">
                    <div class="empty-state-icon">🔗</div>
                    <p>No relations found in the database.</p>
                </div>
"""
    
    html_content += """
            </div>
        </div>
        
        <div id="by-meaning" class="tab-content">
            <div class="search-box">
                <input type="text" id="meaningSearch" placeholder="🔍 Search by meaning..." onkeyup="filterMeaning()">
            </div>
            
            <div class="section" id="meaningContent">
"""
    
    # Add words grouped by meaning
    if words_by_meaning:
        for meaning in sorted(words_by_meaning.keys()):
            word_list = words_by_meaning[meaning]
            html_content += f"""
                <h3>{meaning.title()} ({len(word_list)})</h3>
                <div class="word-grid">
"""
            for word in sorted(word_list, key=lambda x: x['word']):
                tags_html = f'<span class="tag pos">{word["pos_tag"]}</span>' if word['pos_tag'] else ''
                tags_html += f'<span class="tag meaning">{word["meaning_tag"]}</span>'
                if word['is_plural']:
                    tags_html += '<span class="tag plural">plural</span>'
                
                html_content += f"""
                    <div class="word-card">
                        <div class="word">{word['word']}</div>
                        <div class="tags">{tags_html}</div>
                    </div>
"""
            html_content += """
                </div>
"""
    else:
        html_content += """
                <div class="empty-state">
                    <div class="empty-state-icon">🏷️</div>
                    <p>No meaning tags found in the database.</p>
                </div>
"""
    
    html_content += f"""
            </div>
        </div>
        
        <div class="footer">
            Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br>
            Beari AI Database Viewer
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(content => content.classList.remove('active'));
            
            // Deactivate all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Activate selected tab
            event.target.classList.add('active');
        }}
        
        function filterVocabulary() {{
            const input = document.getElementById('vocabSearch');
            const filter = input.value.toLowerCase();
            const cards = document.querySelectorAll('#vocabularyContent .word-card');
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                if (text.includes(filter)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
        
        function filterRelations() {{
            const input = document.getElementById('relSearch');
            const filter = input.value.toLowerCase();
            const items = document.querySelectorAll('#relationsContent .relation-item');
            
            items.forEach(item => {{
                const text = item.textContent.toLowerCase();
                if (text.includes(filter)) {{
                    item.style.display = '';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}
        
        function filterMeaning() {{
            const input = document.getElementById('meaningSearch');
            const filter = input.value.toLowerCase();
            const cards = document.querySelectorAll('#meaningContent .word-card');
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                if (text.includes(filter)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML file generated: {output_file}")
    return output_file


def main():
    """Main entry point."""
    db_path = "beari.db"
    output_file = "beari_database.html"
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("\nBeari Database HTML Export Tool")
            print("="*70)
            print("\nUsage:")
            print("  python export_db_html.py                    # Use default paths")
            print("  python export_db_html.py <db_path>          # Custom database")
            print("  python export_db_html.py <db_path> <output> # Custom paths")
            print("\nExamples:")
            print("  python export_db_html.py")
            print("  python export_db_html.py beari.db")
            print("  python export_db_html.py beari.db my_export.html")
            return
        
        db_path = sys.argv[1]
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
    
    try:
        with DatabaseHelper(db_path) as db:
            print(f"\n📖 Reading database: {db_path}")
            output_path = generate_html(db, output_file)
            print(f"\n🌐 Open the file in your browser:")
            print(f"   {output_path}")
            print("\n" + "="*70 + "\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"Make sure the database file exists at: {db_path}")
        print("Run 'python db/init_db.py' to create it.")


if __name__ == "__main__":
    main()
