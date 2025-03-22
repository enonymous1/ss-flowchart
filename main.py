import graphviz

def create_flowchart():
    dot = graphviz.Digraph(comment='RMF Process', engine='neato')  # Use 'neato' for circular layout
    dot.attr(start='5', normalize='0', layout='neato', fontname='Arial', label='Risk Management Framework Steps', labelloc='t', fontsize='24')
    dot.attr('node', shape='rect', style='rounded,filled', width='1.5', height='1.5', fixedsize='true', color='#00000088', fontname='Helvetica,Arial,sans-serif')
    dot.attr('edge', len='2', penwidth='1.5', arrowhead='open')

    # Define nodes with specific colors
    dot.node('Prepare', 'Prepare', fillcolor='#ADD8E6', fontcolor='black')
    dot.node('Categorize', 'Categorize\nSystem', fillcolor='#90EE90')  # Light Green
    dot.node('Select', 'Select\nControls', fillcolor='#ADFF2F')  # Green Yellow
    dot.node('Implement', 'Implement\nControls', fillcolor='#FFFF00')  # Yellow
    dot.node('Assess', 'Assess\nControls', fillcolor='#FFD700')  # Gold
    dot.node('Authorize', 'Authorize\nSystem', fillcolor='#FFA500')  # Orange
    dot.node('Monitor', 'Monitor\nControls', fillcolor='#FF8C00')  # Dark Orange

    # Define clockwise edges
    dot.edge('Categorize', 'Select', color='gray')
    dot.edge('Select', 'Implement', color='gray')
    dot.edge('Implement', 'Assess', color='gray')
    dot.edge('Assess', 'Authorize', color='gray')
    dot.edge('Authorize', 'Monitor', color='gray')
    dot.edge('Monitor', 'Categorize', color='gray')

    # Define dashed edges from 'Prepare'
    dot.edge('Prepare', 'Categorize', style='dashed', color='black')
    dot.edge('Prepare', 'Select', style='dashed', color='black')
    dot.edge('Prepare', 'Implement', style='dashed', color='black')
    dot.edge('Prepare', 'Assess', style='dashed', color='black')
    dot.edge('Prepare', 'Authorize', style='dashed', color='black')
    dot.edge('Prepare', 'Monitor', style='dashed', color='black')

    # Render the flowchart to a file
    dot.render('rmf_flowchart', format='png', cleanup=True)

if __name__ == "__main__":
    create_flowchart()
