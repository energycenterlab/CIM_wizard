import React from 'react';

const SidebarRight = ({ selectedNode }) => {
  const data = selectedNode?.data;
  return (
  <aside
    style={{
      maxWidth: "250px",     
      width: "100%",          
      padding: "10px",
      overflowY: "auto",      
      borderRight: "1px solid #ccc", 
      backgroundColor: "#f9f9f9",
      display: 'flex',
      flexDirection: 'column',
      alignItems:"flex-start"
    }}
  >
    <div style={{ width: '100%' }}>
      <h3 style={{ marginTop: 0 }}>Details</h3>
      {!data ? (
        <div style={{ color: '#666' }}>Select a node to see details</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div>
            <div style={{ fontWeight: 600 }}>{data.name || data.label}</div>
            {data.description && <div style={{ color: '#666', fontSize: 12, marginTop: 4 }}>{data.description}</div>}
            {data.modelDefId && <div style={{ color: '#666', fontSize: 12 }}>{data.modelDefId}</div>}
          </div>

          {/* Tags */}
          {data.tags && data.tags.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Tags</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {data.tags.map((tag) => (
                  <span key={tag} style={{ background: '#f1f5f9', color: '#334155', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {tag}
                  </span>
                ))}
              </div>
            </section>
          )}

          {/* Solver */}
          {data.solver && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Solver</div>
              <div style={{ color: '#444' }}>{data.solver}</div>
            </section>
          )}

          {/* Execution Command */}
          {data.model_execution_cmd && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Execution Command</div>
              <div style={{ color: '#444', fontFamily: 'monospace', fontSize: 11 }}>{data.model_execution_cmd}</div>
            </section>
          )}

          {/* Simulation Parameters */}
          {data.simulation_parameters && data.simulation_parameters.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Simulation Parameters</div>
              {data.simulation_parameters.map((param, index) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f8fafc', borderRadius: 4 }}>
                  <div style={{ fontWeight: 500, fontSize: 12 }}>{param.name}</div>
                  <div style={{ fontSize: 11, color: '#666' }}>{param.description}</div>
                  <div style={{ fontSize: 11, color: '#444' }}>Value: {param.value} {param.unit}</div>
                </div>
              ))}
            </section>
          )}

          {/* Input Variables */}
          {data.input_variables && data.input_variables.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Input Variables</div>
              {data.input_variables.map((input, index) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0f9ff', borderRadius: 4 }}>
                  <div style={{ fontWeight: 500, fontSize: 12 }}>{input.name}</div>
                  <div style={{ fontSize: 11, color: '#666' }}>{input.description}</div>
                  <div style={{ fontSize: 11, color: '#444' }}>Start: {input.start_value} {input.unit}</div>
                </div>
              ))}
            </section>
          )}

          {/* Output Variables */}
          {data.output_variables && data.output_variables.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Output Variables</div>
              {data.output_variables.map((output, index) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#fef2f2', borderRadius: 4 }}>
                  <div style={{ fontWeight: 500, fontSize: 12 }}>{output.name}</div>
                  <div style={{ fontSize: 11, color: '#666' }}>{output.description}</div>
                  <div style={{ fontSize: 11, color: '#444' }}>Start: {output.start_value} {output.unit}</div>
                </div>
              ))}
            </section>
          )}

          {/* Model Parameters */}
          {data.model_parameters && data.model_parameters.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Model Parameters</div>
              {data.model_parameters.map((param, index) => (
                <div key={index} style={{ marginBottom: 4, padding: 4, background: '#f0fdf4', borderRadius: 4 }}>
                  <div style={{ fontWeight: 500, fontSize: 12 }}>{param.name}</div>
                  <div style={{ fontSize: 11, color: '#666' }}>{param.description}</div>
                  <div style={{ fontSize: 11, color: '#444' }}>Default: {param.default_value} {param.unit}</div>
                </div>
              ))}
            </section>
          )}

          {/* Possible Connections */}
          {data.possible_connections && data.possible_connections.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Possible Connections</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {data.possible_connections.map((connection) => (
                  <span key={connection} style={{ background: '#e0e7ff', color: '#3730a3', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {connection}
                  </span>
                ))}
              </div>
            </section>
          )}

          {/* Components (for composite models) */}
          {data.components && data.components.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Components</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {data.components.map((component) => (
                  <span key={component} style={{ background: '#fef3c7', color: '#92400e', borderRadius: 12, padding: '2px 6px', fontSize: 10 }}>
                    {component}
                  </span>
                ))}
              </div>
            </section>
          )}

          {/* Connections (for composite models) */}
          {data.connections && data.connections.length > 0 && (
            <section>
              <div style={{ fontWeight: 600, marginBottom: 4 }}>Connections</div>
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: 4, padding: 8 }}>
                {data.connections.map((connection, index) => (
                  <div key={index} style={{ fontFamily: 'monospace', fontSize: 10, marginBottom: index < data.connections.length - 1 ? 4 : 0 }}>
                    {connection}
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
    </aside>
  );
};

export default SidebarRight;

function Row({ label, value }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, borderBottom: '1px dashed #eee', padding: '2px 0' }}>
      <div style={{ color: '#555' }}>{label}</div>
      <div style={{ fontWeight: 500 }}>{value}</div>
    </div>
  );
}