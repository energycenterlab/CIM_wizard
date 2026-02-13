import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceArea,
} from 'recharts';
import './SimulationResults.css';
import { apiService } from '../../services/api';
import lineChartIcon from '../../assets/line_chart.svg';
import matrixIcon from '../../assets/matrix.svg';
import gridIcon from '../../assets/grid_chart.svg';
import downloadIcon from '../../assets/download.svg';
import barChartIcon from '../../assets/bar-chart.svg';
import pinListIcon from '../../assets/pin-list.svg';

interface SimulationResultsProps {
  simulationId: string;
  scenarioName?: string;
  selectedHdf5File?: string;
}

interface HDF5File {
  name: string;
  size: string;
  scenario_name?: string;
}

interface DatasetData {
  [entity: string]: {
    [attribute: string]: {
      values: number[];
      unit?: string;
    };
  };
}

interface TimeInfo {
  time_steps?: string[];
}

interface FileData {
  datasets: DatasetData;
  time_info?: TimeInfo;
}

interface AttributeData {
  name: string;
  values: number[];
  color: string;
  unit?: string;
  visible: boolean;
  useRightAxis?: boolean;
}

interface ComponentData {
  name: string;
  category: string;
  attributes: AttributeData[];
  metadata?: Record<string, any>;
}

interface CategoryGroup {
  category: string;
  entities: ComponentData[];
}

interface PinnedSeries {
  entityName: string;
  attributeName: string;
  color: string;
  unit?: string;
}

const colors = [
  '#3B82F6', // blue
  '#EF4444', // red
  '#10B981', // green
  '#F59E0B', // orange
  '#8B5CF6', // purple
  '#06B6D4', // cyan
  '#84CC16', // lime
  '#F97316', // orange
  '#EC4899', // pink
  '#6366F1', // indigo
];

/**
 * Improved category extraction using HDF5 path structure
 */
const extractCategory = (entityName: string, groupPath: string): string => {

  // 2. Use the folder name from the path (e.g., "Series/powernode_proc..." -> "powernode_proc")
  const parts = groupPath.split('/');
  if (parts.length > 1) {
    // Remove numbers or unique IDs to get a clean category (e.g. "powernode_proc_0-0" -> "powernode")
    const rawCategory = parts[1].split(/[._-]/)[0];
    if (rawCategory) {
      return rawCategory.charAt(0).toUpperCase() + rawCategory.slice(1).toLowerCase();
    }
  }

  // 3. Fallback: Handle simple names like "time"
  if (!entityName.includes('_') && !entityName.includes('.')) {
    return entityName.charAt(0).toUpperCase() + entityName.slice(1).toLowerCase();
  }

  // 4. Extract the part before the first dot (if exists)
  const beforeDot = entityName.split('.')[0];
  
  // 5. Check for known patterns
  const powerNodeMatch = beforeDot.match(/powernode|power_node/i);
  if (powerNodeMatch) return 'Power nodes';

  const pvMatch = beforeDot.match(/pv_proc|pv_plant/i);
  if (pvMatch) return 'PV plants';

  const meteoMatch = beforeDot.match(/meteo/i);
  if (meteoMatch) return 'Weather';

  const buildingMatch = beforeDot.match(/building/i);
  if (buildingMatch) return 'Buildings';

  const heatPumpMatch = beforeDot.match(/heat_pump|heatpump/i);
  if (heatPumpMatch) return 'Heat pumps';

  const schedulerMatch = beforeDot.match(/scheduler/i);
  if (schedulerMatch) return 'Schedulers';

  // 6. Fallback to "Other"
  return 'Other';
};

/**
 * Detect if attribute should use right axis based on unit or name
 */
const shouldUseRightAxis = (attrName: string, unit?: string): boolean => {
  const name = attrName.toLowerCase();
  const unitLower = unit?.toLowerCase() || '';
  
  // Temperature typically needs right axis
  if (name.includes('temp') || name.includes('t_') || unitLower.includes('°c') || unitLower.includes('celsius')) {
    return true;
  }
  
  // Humidity
  if (name.includes('humidity') || name.includes('rh') || unitLower.includes('%')) {
    return true;
  }
  
  return false;
};

const SimulationResults: React.FC<SimulationResultsProps> = ({
  simulationId,
  scenarioName,
  selectedHdf5File,
}) => {
  const [hdf5Files, setHdf5Files] = useState<HDF5File[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>(selectedHdf5File || '');
  const [components, setComponents] = useState<ComponentData[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedEntity, setSelectedEntity] = useState<string>('');
  const [pinnedSeries, setPinnedSeries] = useState<PinnedSeries[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [visibleAttributes, setVisibleAttributes] = useState<Set<string>>(new Set());
  
  // Chart view state
  const [chartView, setChartView] = useState<'line' | 'matrix'>('line');
  const [xAxisScale, setXAxisScale] = useState<'linear' | 'log' | 'symlog'>('linear');
  const [yAxisScale, setYAxisScale] = useState<'linear' | 'log' | 'symlog'>('linear');
  const [showGrid, setShowGrid] = useState(true);
  const [visualizationType, setVisualizationType] = useState<'line' | 'bar'>('line');
  const [dataDisplay, setDataDisplay] = useState<'line' | 'point' | 'both'>('line');
  const [cellWidth, setCellWidth] = useState<number>(80);
  const [notation, setNotation] = useState<'scientific' | 'exact'>('exact');
  
  // Zoom state
  const [zoomDomain, setZoomDomain] = useState<{ x?: [number, number]; y?: [number, number] } | null>(null);
  const [zoomLevel, setZoomLevel] = useState<number>(1); // 1 = no zoom, >1 = zoomed in
  const [zoomCenter, setZoomCenter] = useState<number | null>(null); // Center point for zoom
  const touchStartDistance = useRef<number | null>(null);
  const touchStartCenter = useRef<number | null>(null);
  const [showAspectMenu, setShowAspectMenu] = useState(false);
  const [showXAxisMenu, setShowXAxisMenu] = useState(false);
  const [showYAxisMenu, setShowYAxisMenu] = useState(false);
  const [showZoomHelp, setShowZoomHelp] = useState(false);
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState<{ x: number; time: number } | null>(null);
  const chartRef = useRef<any>(null);
  const chartContainerRef = useRef<HTMLDivElement>(null);

  // Close dropdown menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.data-visualization-dropdown')) {
        setShowAspectMenu(false);
      }
      if (!target.closest('.x-axis-dropdown')) {
        setShowXAxisMenu(false);
      }
      if (!target.closest('.y-axis-dropdown')) {
        setShowYAxisMenu(false);
      }
      if (!target.closest('.zoom-help-container')) {
        setShowZoomHelp(false);
      }
    };
    
    if (showAspectMenu || showXAxisMenu || showYAxisMenu || showZoomHelp) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showAspectMenu, showXAxisMenu, showYAxisMenu, showZoomHelp]);

  // Group components by category
  const categoryGroups = useMemo<CategoryGroup[]>(() => {
    const categoryMap = new Map<string, ComponentData[]>();
    
    components.forEach((comp) => {
      if (!categoryMap.has(comp.category)) {
        categoryMap.set(comp.category, []);
      }
      categoryMap.get(comp.category)!.push(comp);
    });

    // Sort categories: time first, then alphabetically
    const sortedCategories = Array.from(categoryMap.keys()).sort((a, b) => {
      if (a === 'time') return -1;
      if (b === 'time') return 1;
      return a.localeCompare(b);
    });

    return sortedCategories.map((category) => ({
      category,
      entities: categoryMap.get(category)!,
    }));
  }, [components]);

  // Auto-select first category and entity when categories change
  useEffect(() => {
    if (categoryGroups.length > 0 && !selectedCategory) {
      const firstCategory = categoryGroups[0];
      setSelectedCategory(firstCategory.category);
      if (firstCategory.entities.length > 0) {
        setSelectedEntity(firstCategory.entities[0].name);
        // Initialize visible attributes
        const attrs = firstCategory.entities[0].attributes.map(a => a.name);
        setVisibleAttributes(new Set(attrs));
      }
    }
  }, [categoryGroups, selectedCategory]);

  // Auto-select first entity when category changes
  useEffect(() => {
    const categoryGroup = categoryGroups.find((g) => g.category === selectedCategory);
    if (categoryGroup && categoryGroup.entities.length > 0) {
      if (!categoryGroup.entities.find((e) => e.name === selectedEntity)) {
        const firstEntity = categoryGroup.entities[0];
        setSelectedEntity(firstEntity.name);
        setVisibleAttributes(new Set(firstEntity.attributes.map(a => a.name)));
      }
    }
  }, [selectedCategory, categoryGroups, selectedEntity]);

  // Update selectedFile when selectedHdf5File prop changes
  useEffect(() => {
    if (selectedHdf5File) {
      // Reset component state when file changes
      setComponents([]);
      setSelectedCategory('');
      setSelectedEntity('');
      setPinnedSeries([]);
      setError(null);
      setZoomDomain(null);
      setZoomLevel(1);
      setZoomCenter(null);
      setVisibleAttributes(new Set());
      // Update selected file
      setSelectedFile(selectedHdf5File);
      // Set a placeholder in hdf5Files array so the component doesn't show "No results available"
      // The actual file data will be loaded by the loadFileData effect
      setHdf5Files([{ name: selectedHdf5File, size: '', scenario_name: '' }]);
    }
  }, [selectedHdf5File]);

  // Load HDF5 files when simulationId changes (if selectedHdf5File is not provided)
  useEffect(() => {
    if (!selectedHdf5File && simulationId) {
      // Reset all state when simulationId changes
      setHdf5Files([]);
      setSelectedFile('');
      setComponents([]);
      setSelectedCategory('');
      setSelectedEntity('');
      setPinnedSeries([]);
      setError(null);
      setZoomDomain(null);
      setZoomLevel(1);
      setZoomCenter(null);
      setVisibleAttributes(new Set());
      
      // Load new simulation's files - define inline to ensure latest simulationId
      const loadFiles = async () => {
        try {
          const data = await apiService.getSimulationResults(simulationId);
          const files = data.hdf5_files || [];
          setHdf5Files(files);
          if (files.length > 0) {
            setSelectedFile(files[0].name);
          }
        } catch (err) {
          setError('Error loading HDF5 files');
          console.error(err);
        }
      };
      
      loadFiles();
    }
  }, [simulationId, selectedHdf5File]);

  useEffect(() => {
    if (selectedFile && simulationId) {
      // Define loadFileData inline to ensure latest simulationId
      const loadData = async () => {
        if (!selectedFile) return;

        setLoading(true);
        setError(null);

        try {
          const fileInfo = await apiService.getSimulationFileInfo(simulationId, selectedFile);
          const groups = fileInfo.groups || {};
          const attributes = fileInfo.attributes || {};

          // Extract components from Series groups
          const componentNames: string[] = [];
          Object.keys(groups).forEach((groupPath) => {
            if (groupPath.startsWith('Series/') && groupPath !== 'Series') {
              const componentName = groupPath.replace('Series/', '');
              componentNames.push(componentName);
            }
          });

          if (componentNames.length === 0) {
            setError('No components found in HDF5 file');
            setLoading(false);
            return;
          }

          // Build dataset paths for all components
          const allDatasetPaths: string[] = [];
          componentNames.forEach((compName) => {
            const groupPath = `Series/${compName}`;
            const groupInfo = groups[groupPath];
            const attrs = groupInfo?.items || [];
            attrs.forEach((attr: string) => {
              allDatasetPaths.push(`${groupPath}/${attr}`);
            });
          });

          // Load all data at once
          const datasetsParam = allDatasetPaths.join(',');
          const fileData: FileData = await apiService.getSimulationFileData(simulationId, selectedFile, datasetsParam);
          const datasets = fileData.datasets || {};
          const timeSteps = fileData.time_info?.time_steps || [];

          // Process components with category extraction and unit detection
          const colors = ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'];
          const processedComponents: ComponentData[] = componentNames.map((compName) => {
            const groupPath = `Series/${compName}`;
            const category = extractCategory(compName, groupPath);
            const groupInfo = groups[groupPath];
            const attrs = groupInfo?.items || [];
            const groupAttrs = groupInfo?.attributes || {};

            const attributeData: AttributeData[] = attrs.map((attrName: string, attrIndex: number) => {
              const entityData = datasets[compName];
              const attrData = entityData?.[attrName];
              const values = attrData?.values || [];

              const unit = attrData?.unit || groupAttrs[attrName]?.unit || '';

              return {
                name: attrName,
                values: Array.isArray(values) ? values : [values],
                color: colors[attrIndex % colors.length],
                unit,
                visible: true,
                useRightAxis: shouldUseRightAxis(attrName, unit),
              };
            });

            return {
              name: compName,
              category,
              attributes: attributeData.filter((attr) => attr.values.length > 0),
              metadata: groupAttrs,
            };
          }).filter((comp) => comp.attributes.length > 0);

          setComponents(processedComponents);
          setLoading(false);
        } catch (err) {
          setError('Error loading file data');
          console.error(err);
          setLoading(false);
        }
      };
      
      loadData();
    }
  }, [selectedFile, simulationId]);

  // Attach wheel event to recharts-responsive-container
  useEffect(() => {
    if (!chartContainerRef.current || chartView !== 'line' || !selectedEntity) return;

    const findRechartsContainer = (): HTMLElement | null => {
      return chartContainerRef.current?.querySelector('.recharts-responsive-container') as HTMLElement || null;
    };

    let rechartsContainer: HTMLElement | null = null;
    let cleanup: (() => void) | null = null;

    const attachListener = () => {
      rechartsContainer = findRechartsContainer();
      if (!rechartsContainer) return;

      const handleWheelNative = (e: WheelEvent) => {
        // Always prevent default when inside recharts container
        e.preventDefault();
        e.stopPropagation();
        
        // Get component and data for zoom calculation
        const component = components.find(c => c.name === selectedEntity);
        if (!component) return;

        const timeSteps = Array.from(
          { length: Math.max(...component.attributes.map((attr) => attr.values.length)) },
          (_, i) => i.toString()
        );
        
        const prepareChartData = (comp: ComponentData, steps: string[]) => {
          const rawLength = Math.max(...comp.attributes.map((attr) => attr.values.length));
          const chartData: any[] = [];
          for (let i = 0; i < rawLength; i++) {
            const dataPoint: any = { time: steps[i] || i.toString() };
            comp.attributes.forEach((attr) => {
              dataPoint[`${comp.name}.${attr.name}`] = attr.values[i] ?? null;
            });
            chartData.push(dataPoint);
          }
          return chartData;
        };

        const fullChartData = prepareChartData(component, timeSteps);
        if (fullChartData.length === 0) return;

        const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
        const minTime = Math.min(...timeValues);
        const maxTime = Math.max(...timeValues);
        const totalRange = maxTime - minTime;
        
        // Get mouse position relative to chart
        const rect = rechartsContainer!.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const chartWidth = rect.width;
        
        // Calculate the time at mouse position
        const currentDomain = zoomDomain?.x || [minTime, maxTime];
        const currentRange = currentDomain[1] - currentDomain[0];
        const mouseTime = currentDomain[0] + (mouseX / chartWidth) * currentRange;
        
        // Zoom factor (positive = zoom in, negative = zoom out)
        // Reduced sensitivity: smaller factors for more gradual zoom
        const zoomFactor = e.deltaY > 0 ? 1.05 : 0.95;
        const newRange = Math.max(totalRange * 0.01, Math.min(totalRange, currentRange * zoomFactor));
        
        // Calculate new domain centered on mouse position
        const newMin = Math.max(minTime, mouseTime - (mouseX / chartWidth) * newRange);
        const newMax = Math.min(maxTime, newMin + newRange);
        
        // Adjust if we hit boundaries
        const adjustedMin = newMax >= maxTime ? maxTime - newRange : newMin;
        const finalMin = Math.max(minTime, adjustedMin);
        const finalMax = Math.min(maxTime, finalMin + newRange);
        
        if (finalMax > finalMin && newRange < totalRange) {
          setZoomDomain({ x: [finalMin, finalMax] });
          setZoomLevel(newRange / totalRange);
          setZoomCenter(mouseTime);
        } else if (newRange >= totalRange) {
          // Reset to full view
          setZoomDomain(null);
          setZoomLevel(1);
          setZoomCenter(null);
        }
      };

      // Use { passive: false } to allow preventDefault
      rechartsContainer.addEventListener('wheel', handleWheelNative, { passive: false });
      
      cleanup = () => {
        rechartsContainer?.removeEventListener('wheel', handleWheelNative);
      };
    };

    // Try immediately
    attachListener();

    // If not found, try after a delay (Recharts might not be rendered yet)
    if (!rechartsContainer) {
      const timeout = setTimeout(attachListener, 100);
      return () => {
        clearTimeout(timeout);
        if (cleanup) cleanup();
      };
    }

    return () => {
      if (cleanup) cleanup();
    };
  }, [components, selectedEntity, chartView, zoomDomain]);

  const loadHDF5Files = async () => {
    try {
      const data = await apiService.getSimulationResults(simulationId);
      const files = data.hdf5_files || [];
      setHdf5Files(files);
      if (files.length > 0) {
        setSelectedFile(files[0].name);
      }
    } catch (err) {
      setError('Error loading HDF5 files');
      console.error(err);
    }
  };


  const loadFileData = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setError(null);

    try {
      const fileInfo = await apiService.getSimulationFileInfo(simulationId, selectedFile);
      const groups = fileInfo.groups || {};
      const attributes = fileInfo.attributes || {};


      // Extract components from Series groups
      const componentNames: string[] = [];
      Object.keys(groups).forEach((groupPath) => {
        if (groupPath.startsWith('Series/') && groupPath !== 'Series') {
          const componentName = groupPath.replace('Series/', '');
          componentNames.push(componentName);
        }
      });

      if (componentNames.length === 0) {
        setError('No components found in HDF5 file');
        setLoading(false);
        return;
      }

      // Build dataset paths for all components
      const allDatasetPaths: string[] = [];
      componentNames.forEach((compName) => {
        const groupPath = `Series/${compName}`;
        const groupInfo = groups[groupPath];
        const attrs = groupInfo?.items || [];
        attrs.forEach((attr: string) => {
          allDatasetPaths.push(`${groupPath}/${attr}`);
        });
      });

      // Load all data at once
      const datasetsParam = allDatasetPaths.join(',');
      const fileData: FileData = await apiService.getSimulationFileData(simulationId, selectedFile, datasetsParam);
      const datasets = fileData.datasets || {};
      const timeSteps = fileData.time_info?.time_steps || [];

      // Process components with category extraction and unit detection
      const processedComponents: ComponentData[] = componentNames.map((compName) => {
        const groupPath = `Series/${compName}`;
        const category = extractCategory(compName, groupPath);
        const groupInfo = groups[groupPath];
        const attrs = groupInfo?.items || [];
        const groupAttrs = groupInfo?.attributes || {};

        const attributeData: AttributeData[] = attrs.map((attr: string, attrIndex: number) => {
          const entityData = datasets[compName];
          const attrData = entityData?.[attr];
          const values = attrData?.values || [];
          const unit = attrData?.unit || groupAttrs[attr]?.unit;

          return {
            name: attr,
            values: Array.isArray(values) ? values : [values],
            color: colors[attrIndex % colors.length],
            unit,
            visible: true,
            useRightAxis: shouldUseRightAxis(attr, unit),
          };
        });

        return {
          name: compName,
          category,
          attributes: attributeData.filter((attr) => attr.values.length > 0),
          metadata: groupAttrs,
        };
      }).filter((comp) => comp.attributes.length > 0);

      setComponents(processedComponents);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading file data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleAttributeVisibility = (attrName: string) => {
    const newVisible = new Set(visibleAttributes);
    if (newVisible.has(attrName)) {
      newVisible.delete(attrName);
    } else {
      newVisible.add(attrName);
    }
    setVisibleAttributes(newVisible);
  };

  const pinSeries = (entityName: string, attributeName: string) => {
    // Check if already pinned
    const isAlreadyPinned = pinnedSeries.some(
      (p) => p.entityName === entityName && p.attributeName === attributeName
    );
    if (isAlreadyPinned) return;

    const component = components.find((c) => c.name === entityName);
    const attr = component?.attributes.find((a) => a.name === attributeName);
    if (attr) {
      setPinnedSeries([
        ...pinnedSeries,
        {
          entityName,
          attributeName,
          color: attr.color,
          unit: attr.unit,
        },
      ]);
    }
  };

  const isPinned = (entityName: string, attributeName: string): boolean => {
    return pinnedSeries.some(
      (p) => p.entityName === entityName && p.attributeName === attributeName
    );
  };

  const unpinSeries = (entityName: string, attributeName: string) => {
    setPinnedSeries(
      pinnedSeries.filter(
        (p) => !(p.entityName === entityName && p.attributeName === attributeName)
      )
    );
  };

  const prepareChartData = (component: ComponentData, timeSteps: string[]) => {
    const rawLength = Math.max(
      ...component.attributes.map((attr) => attr.values.length),
      ...pinnedSeries.map(() => {
        const pinnedComp = components.find((c) => c.name === pinnedSeries[0]?.entityName);
        const pinnedAttr = pinnedComp?.attributes.find((a) => a.name === pinnedSeries[0]?.attributeName);
        return pinnedAttr?.values.length || 0;
      })
    );

    // FIX: Data Decimation - If we have > 2000 points, take every Nth point to prevent "dots" visualization issue
    const threshold = 2000;
    const step = rawLength > threshold ? Math.ceil(rawLength / threshold) : 1;

    const data = [];
    for (let i = 0; i < rawLength; i += step) {
      const point: any = {
        // If timeSteps are just indices, format them nicely
        time: timeSteps[i] ? parseFloat(timeSteps[i]).toFixed(2) : i.toString(),
        fullTime: timeSteps[i] // Keep full resolution for tooltip if needed
      };

      // Add visible attributes from selected component
      component.attributes.forEach((attr) => {
        if (visibleAttributes.has(attr.name) && attr.visible) {
          // FIX: Handle sparse data - use null for undefined/NaN values
          const val = attr.values[i];
          point[`${component.name}.${attr.name}`] = (val === undefined || isNaN(val)) ? null : val;
        }
      });

      // Add pinned series
      pinnedSeries.forEach((pinned) => {
        const pinnedComp = components.find((c) => c.name === pinned.entityName);
        const pinnedAttr = pinnedComp?.attributes.find((a) => a.name === pinned.attributeName);
        if (pinnedAttr) {
          const key = `[PINNED] ${pinned.entityName}.${pinned.attributeName}`;
          const val = pinnedAttr.values[i];
          point[key] = (val === undefined || isNaN(val)) ? null : val;
        }
      });

      data.push(point);
    }

    return data;
  };

  const renderChart = (component: ComponentData) => {
    if (!component.attributes.length) return null;

    const visibleAttrs = component.attributes.filter(
      (attr) => visibleAttributes.has(attr.name) && attr.visible
    );

    const isEmptySelection = visibleAttrs.length === 0 && pinnedSeries.length === 0;

    const timeSteps = Array.from(
      { length: Math.max(...component.attributes.map((attr) => attr.values.length)) },
      (_, i) => i.toString()
    );

    const fullChartData = isEmptySelection ? [] : prepareChartData(component, timeSteps);
    
    // For log scale, ensure no zero or negative values
    const safeChartData = (yAxisScale === 'log' || xAxisScale === 'log') 
      ? fullChartData.map((d: any) => {
          const safeD: any = { ...d };
          visibleAttrs.forEach(attr => {
            const key = `${component.name}.${attr.name}`;
            if (safeD[key] !== undefined && safeD[key] <= 0) {
              safeD[key] = 1e-10; // Minimum epsilon for log scale
            }
          });
          return safeD;
        })
      : fullChartData;
    
    const hasRightAxis = visibleAttrs.some((attr) => attr.useRightAxis) ||
      pinnedSeries.some((p) => {
        const comp = components.find((c) => c.name === p.entityName);
        const attr = comp?.attributes.find((a) => a.name === p.attributeName);
        return attr?.useRightAxis;
      });

    // Mouse wheel zoom - this will be attached to recharts container via useEffect
    const handleWheelZoom = (e: WheelEvent, fullChartData: any[]) => {
      // Always prevent default when inside recharts container
      e.preventDefault();
      e.stopPropagation();
      
      if (fullChartData.length === 0) return;
      
      const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
      const minTime = Math.min(...timeValues);
      const maxTime = Math.max(...timeValues);
      const totalRange = maxTime - minTime;
      
      // Get mouse position relative to chart
      const target = e.currentTarget as HTMLElement;
      const rect = target.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const chartWidth = rect.width;
      
      // Calculate the time at mouse position
      const currentDomain = zoomDomain?.x || [minTime, maxTime];
      const currentRange = currentDomain[1] - currentDomain[0];
      const mouseTime = currentDomain[0] + (mouseX / chartWidth) * currentRange;
      
      // Zoom factor (positive = zoom in, negative = zoom out)
      // Reduced sensitivity: smaller factors for more gradual zoom
      const zoomFactor = e.deltaY > 0 ? 1.05 : 0.95;
      const newRange = Math.max(totalRange * 0.01, Math.min(totalRange, currentRange * zoomFactor));
      
      // Calculate new domain centered on mouse position
      const newMin = Math.max(minTime, mouseTime - (mouseX / chartWidth) * newRange);
      const newMax = Math.min(maxTime, newMin + newRange);
      
      // Adjust if we hit boundaries
      const adjustedMin = newMax >= maxTime ? maxTime - newRange : newMin;
      const finalMin = Math.max(minTime, adjustedMin);
      const finalMax = Math.min(maxTime, finalMin + newRange);
      
      if (finalMax > finalMin && newRange < totalRange) {
        setZoomDomain({ x: [finalMin, finalMax] });
        setZoomLevel(newRange / totalRange);
        setZoomCenter(mouseTime);
      } else if (newRange >= totalRange) {
        // Reset to full view
        resetZoom();
      }
    };

    // Touch/pinch zoom
    const handleTouchStart = (e: React.TouchEvent) => {
      if (e.touches.length === 2) {
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        );
        touchStartDistance.current = distance;
        
        // Calculate center point in time coordinates
        const rect = e.currentTarget.getBoundingClientRect();
        const centerX = (touch1.clientX + touch2.clientX) / 2 - rect.left;
        const chartWidth = rect.width;
        
        if (fullChartData.length > 0) {
          const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
          const minTime = Math.min(...timeValues);
          const maxTime = Math.max(...timeValues);
          const currentDomain = zoomDomain?.x || [minTime, maxTime];
          const currentRange = currentDomain[1] - currentDomain[0];
          const centerTime = currentDomain[0] + (centerX / chartWidth) * currentRange;
          touchStartCenter.current = centerTime;
        }
      }
    };

    const handleTouchMove = (e: React.TouchEvent) => {
      if (e.touches.length === 2 && touchStartDistance.current !== null && touchStartCenter.current !== null) {
        e.preventDefault();
        
        const touch1 = e.touches[0];
        const touch2 = e.touches[1];
        const distance = Math.hypot(
          touch2.clientX - touch1.clientX,
          touch2.clientY - touch1.clientY
        );
        
        const rawScale = distance / touchStartDistance.current;
        // Reduce pinch zoom sensitivity by applying a damping factor
        // Map scale from [0.5, 2.0] to [0.95, 1.05] for more gradual zoom
        const scale = rawScale < 1 
          ? 1 - (1 - rawScale) * 0.1  // Zoom out: dampen by 10%
          : 1 + (rawScale - 1) * 0.1; // Zoom in: dampen by 10%
        
        if (fullChartData.length > 0) {
          const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
          const minTime = Math.min(...timeValues);
          const maxTime = Math.max(...timeValues);
          const totalRange = maxTime - minTime;
          
          const currentDomain = zoomDomain?.x || [minTime, maxTime];
          const currentRange = currentDomain[1] - currentDomain[0];
          const newRange = Math.max(totalRange * 0.01, Math.min(totalRange, currentRange / scale));
          
          // Calculate new domain centered on pinch center
          const centerTime = touchStartCenter.current;
          const rect = e.currentTarget.getBoundingClientRect();
          const centerX = (touch1.clientX + touch2.clientX) / 2 - rect.left;
          const chartWidth = rect.width;
          
          const newMin = Math.max(minTime, centerTime - (centerX / chartWidth) * newRange);
          const newMax = Math.min(maxTime, newMin + newRange);
          
          const adjustedMin = newMax >= maxTime ? maxTime - newRange : newMin;
          const finalMin = Math.max(minTime, adjustedMin);
          const finalMax = Math.min(maxTime, finalMin + newRange);
          
          if (finalMax > finalMin) {
            setZoomDomain({ x: [finalMin, finalMax] });
            setZoomLevel(newRange / totalRange);
          }
        }
      }
    };

    const handleTouchEnd = () => {
      touchStartDistance.current = null;
      touchStartCenter.current = null;
    };

    const resetZoom = () => {
      setZoomDomain(null);
      setZoomLevel(1);
      setZoomCenter(null);
      setIsPanning(false);
      setPanStart(null);
    };

    // Pan functionality (click and drag when zoomed)
    const handlePanStart = (e: React.MouseEvent) => {
      if (!zoomDomain || fullChartData.length === 0) return;
      
      // Prevent default to avoid text selection and other interactions
      e.preventDefault();
      e.stopPropagation();
      
      const rect = e.currentTarget.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const chartWidth = rect.width;
      
      const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
      const minTime = Math.min(...timeValues);
      const maxTime = Math.max(...timeValues);
      
      const currentDomain = zoomDomain.x || [minTime, maxTime];
      const currentRange = currentDomain[1] - currentDomain[0];
      const mouseTime = currentDomain[0] + (mouseX / chartWidth) * currentRange;
      
      setIsPanning(true);
      setPanStart({ x: mouseX, time: mouseTime });
      
      // Prevent text selection during pan
      document.body.style.userSelect = 'none';
      document.body.style.cursor = 'grabbing';
    };

    const handlePanMove = (e: React.MouseEvent) => {
      if (!isPanning || !panStart || !zoomDomain || fullChartData.length === 0) return;
      
      // Prevent default to avoid interactions
      e.preventDefault();
      e.stopPropagation();
      
      const rect = e.currentTarget.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const chartWidth = rect.width;
      
      const timeValues = fullChartData.map((d: any) => parseFloat(d.time));
      const minTime = Math.min(...timeValues);
      const maxTime = Math.max(...timeValues);
      
      const currentDomain = zoomDomain.x || [minTime, maxTime];
      const currentRange = currentDomain[1] - currentDomain[0];
      const currentMouseTime = currentDomain[0] + (mouseX / chartWidth) * currentRange;
      
      // Calculate the time difference
      const timeDelta = panStart.time - currentMouseTime;
      
      // Calculate new domain
      const newMin = Math.max(minTime, currentDomain[0] + timeDelta);
      const newMax = Math.min(maxTime, newMin + currentRange);
      
      // Adjust if we hit boundaries
      const adjustedMin = newMax >= maxTime ? maxTime - currentRange : newMin;
      const finalMin = Math.max(minTime, adjustedMin);
      const finalMax = Math.min(maxTime, finalMin + currentRange);
      
      if (finalMax > finalMin) {
        setZoomDomain({ x: [finalMin, finalMax] });
        // Update pan start to current position for smooth dragging
        setPanStart({ x: mouseX, time: currentMouseTime });
      }
    };

    const handlePanEnd = (e?: React.MouseEvent) => {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      
      setIsPanning(false);
      setPanStart(null);
      
      // Restore text selection
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    };

    const formatValue = (value: number): string => {
      if (notation === 'scientific') {
        return value.toExponential(2);
      }
      return value.toString();
    };

    const exportToCSV = () => {
      const exportData = (yAxisScale === 'log' || xAxisScale === 'log') ? safeChartData : fullChartData;
      const headers = ['Time', ...visibleAttrs.map(attr => `${attr.name}${attr.unit ? ` (${attr.unit})` : ''}`)];
      const rows = exportData.map((row: any) => {
        const values = [row.time, ...visibleAttrs.map(attr => formatValue(row[`${component.name}.${attr.name}`] || 0))];
        return values.join(',');
      });
      const csv = [headers.join(','), ...rows].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${component.name}_data.csv`;
      a.click();
      URL.revokeObjectURL(url);
    };

    const baseData = (yAxisScale === 'log' || xAxisScale === 'log') ? safeChartData : fullChartData;
    const displayData = zoomDomain?.x 
      ? baseData.filter((d: any) => {
          const timeVal = parseFloat(d.time);
          return timeVal >= zoomDomain.x![0] && timeVal <= zoomDomain.x![1];
        })
      : baseData;

    return (
      <div className="results-chart">
        {/* Chart Management Bar */}
        <div className="chart-management-bar">
          <div className="chart-view-tabs">
            <button
              className={`chart-view-tab ${chartView === 'line' ? 'active' : ''}`}
              onClick={() => setChartView('line')}
            >
              <img src={lineChartIcon} alt="Line" className="chart-icon" />
              Line
            </button>
            <button
              className={`chart-view-tab ${chartView === 'matrix' ? 'active' : ''}`}
              onClick={() => setChartView('matrix')}
            >
              <img src={matrixIcon} alt="Matrix" className="chart-icon" />
              Matrix
            </button>
          </div>

          {chartView === 'matrix' && (
            <div className="matrix-controls">
              <label>
                Cell width:
                <input
                  type="number"
                  value={cellWidth}
                  onChange={(e) => setCellWidth(Number(e.target.value))}
                  min={50}
                  max={200}
                  className="cell-width-input"
                />
              </label>
              <label className="notation-label-group">
                Notation:
                <div className="notation-toggle-group">
                  <button
                    className={`notation-toggle-btn ${notation === 'exact' ? 'active' : ''}`}
                    onClick={() => setNotation('exact')}
                  >
                    Exact
                  </button>
                  <button
                    className={`notation-toggle-btn ${notation === 'scientific' ? 'active' : ''}`}
                    onClick={() => setNotation('scientific')}
                  >
                    Scientific
                  </button>
                </div>
              </label>
              <button onClick={exportToCSV} className="export-btn">
                <img src={downloadIcon} alt="Export" className="icon-small" />
                Export
              </button>
            </div>
          )}

          {chartView === 'line' && (
            <div className="line-controls">
              <div className="x-axis-dropdown">
                <button 
                  className="axis-dropdown-trigger"
                  onClick={() => {
                    setShowXAxisMenu(!showXAxisMenu);
                    setShowYAxisMenu(false);
                    setShowAspectMenu(false);
                  }}
                >
                  X: {xAxisScale.charAt(0).toUpperCase() + xAxisScale.slice(1)}
                </button>
                {showXAxisMenu && (
                  <div className="axis-dropdown-menu">
                    <div className="axis-dropdown-toggle">
                      <button
                        className={`axis-dropdown-btn ${xAxisScale === 'linear' ? 'active' : ''}`}
                        onClick={() => {
                          setXAxisScale('linear');
                          setShowXAxisMenu(false);
                        }}
                      >
                        Linear
                      </button>
                      <button
                        className={`axis-dropdown-btn ${xAxisScale === 'log' ? 'active' : ''}`}
                        onClick={() => {
                          setXAxisScale('log');
                          setShowXAxisMenu(false);
                        }}
                      >
                        Log
                      </button>
                      <button
                        className={`axis-dropdown-btn ${xAxisScale === 'symlog' ? 'active' : ''}`}
                        onClick={() => {
                          setXAxisScale('symlog');
                          setShowXAxisMenu(false);
                        }}
                      >
                        Symlog
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <div className="y-axis-dropdown">
                <button 
                  className="axis-dropdown-trigger"
                  onClick={() => {
                    setShowYAxisMenu(!showYAxisMenu);
                    setShowXAxisMenu(false);
                    setShowAspectMenu(false);
                  }}
                >
                  Y: {yAxisScale.charAt(0).toUpperCase() + yAxisScale.slice(1)}
                </button>
                {showYAxisMenu && (
                  <div className="axis-dropdown-menu">
                    <div className="axis-dropdown-toggle">
                      <button
                        className={`axis-dropdown-btn ${yAxisScale === 'linear' ? 'active' : ''}`}
                        onClick={() => {
                          setYAxisScale('linear');
                          setShowYAxisMenu(false);
                        }}
                      >
                        Linear
                      </button>
                      <button
                        className={`axis-dropdown-btn ${yAxisScale === 'log' ? 'active' : ''}`}
                        onClick={() => {
                          setYAxisScale('log');
                          setShowYAxisMenu(false);
                        }}
                      >
                        Log
                      </button>
                      <button
                        className={`axis-dropdown-btn ${yAxisScale === 'symlog' ? 'active' : ''}`}
                        onClick={() => {
                          setYAxisScale('symlog');
                          setShowYAxisMenu(false);
                        }}
                      >
                        Symlog
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <button
                className={`grid-toggle ${showGrid ? 'active' : ''}`}
                onClick={() => setShowGrid(!showGrid)}
              >
                <img src={gridIcon} alt="Grid" className="icon-small" />
                Grid
              </button>
              <div className="data-visualization-dropdown">
                <button 
                  className="data-visualization-trigger"
                  onClick={() => {
                    setShowAspectMenu(!showAspectMenu);
                    setShowXAxisMenu(false);
                    setShowYAxisMenu(false);
                  }}
                >
                  Data Visualization
                </button>
                {showAspectMenu && (
                  <div className="data-visualization-menu">
                    <div className="data-visualization-toggle">
                      <button
                        className={`data-vis-btn ${dataDisplay === 'line' ? 'active' : ''}`}
                        onClick={() => setDataDisplay('line')}
                      >
                        Line
                      </button>
                      <button
                        className={`data-vis-btn ${dataDisplay === 'point' ? 'active' : ''}`}
                        onClick={() => setDataDisplay('point')}
                      >
                        Point
                      </button>
                      <button
                        className={`data-vis-btn ${dataDisplay === 'both' ? 'active' : ''}`}
                        onClick={() => setDataDisplay('both')}
                      >
                        Both
                      </button>
                    </div>
                  </div>
                )}
              </div>
              <div className="zoom-help-container">
                <button
                  className="zoom-help-btn"
                  onClick={() => setShowZoomHelp(!showZoomHelp)}
                  title="Zoom Help"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.5"/>
                    <text x="8" y="11" textAnchor="middle" fontSize="10" fill="currentColor" fontWeight="bold">?</text>
                  </svg>
                </button>
                {showZoomHelp && (
                  <div className="zoom-help-popup">
                    <h4>Zoom & Pan Controls</h4>
                    <ul>
                      <li><strong>Zoom In:</strong> Scroll up or pinch out</li>
                      <li><strong>Zoom Out:</strong> Scroll down or pinch in</li>
                      <li><strong>Pan:</strong> Click and drag to move around when zoomed</li>
                      <li><strong>Reset:</strong> Click "Zoom Reset" to return to full view</li>
                    </ul>
                  </div>
                )}
              </div>
              <button
                className={`zoom-reset-management-btn ${!zoomDomain ? 'disabled' : ''}`}
                onClick={resetZoom}
                disabled={!zoomDomain}
                title={zoomDomain ? "Reset Zoom" : "Zoom in to enable reset"}
              >
                Zoom Reset
              </button>
            </div>
          )}
        </div>

        <div className="results-chart-scrollable">
          {/* Pinned Series */}
          {pinnedSeries.length > 0 && (
            <div className="pinned-series-section">
              <div className="pinned-series-label">Comparison</div>
              <div className="pinned-list">
                {pinnedSeries.map((pinned) => (
                  <div key={`${pinned.entityName}-${pinned.attributeName}`} className="pinned-badge">
                    <span
                      className="pinned-badge-color"
                      style={{ backgroundColor: pinned.color }}
                    />
                    <span className="pinned-badge-name">
                      {pinned.entityName}.{pinned.attributeName}
                      {pinned.unit && <span className="pinned-badge-unit"> ({pinned.unit})</span>}
                    </span>
                    <button
                      className="pinned-badge-close"
                      onClick={() => unpinSeries(pinned.entityName, pinned.attributeName)}
                      title="Unpin"
                      aria-label="Unpin series"
                    >
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 3L3 9M3 3L9 9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

        {/* Chart or Matrix View */}
        {chartView === 'matrix' ? (
          <div className="matrix-view">
            {isEmptySelection ? (
              <div className="chart-empty chart-empty-matrix">
                <p>No visible series. Select attributes to display.</p>
              </div>
            ) : (
              <table className="matrix-table" style={{ width: `${cellWidth * (visibleAttrs.length + 1)}px` }}>
                <thead>
                  <tr>
                    <th>Time</th>
                    {visibleAttrs.map(attr => (
                      <th key={attr.name} style={{ width: `${cellWidth}px` }}>
                        {attr.name}
                        {attr.unit && <span className="unit"> ({attr.unit})</span>}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayData.slice(0, 100).map((row: any, idx: number) => (
                    <tr key={idx}>
                      <td>{row.time}</td>
                      {visibleAttrs.map(attr => (
                        <td key={attr.name} style={{ width: `${cellWidth}px` }}>
                          {formatValue(row[`${component.name}.${attr.name}`] || 0)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        ) : (
          <div className="chart-wrapper">
            <div 
              ref={chartContainerRef}
              className={`chart-container ${isPanning ? 'panning' : ''}`}
              style={{ position: 'relative', cursor: isPanning ? 'grabbing' : (zoomDomain ? 'grab' : 'default') }}
              onMouseDown={handlePanStart}
              onMouseMove={handlePanMove}
              onMouseUp={handlePanEnd}
              onMouseLeave={handlePanEnd}
              onTouchStart={handleTouchStart}
              onTouchMove={handleTouchMove}
              onTouchEnd={handleTouchEnd}
            >
              {isEmptySelection && (
                <div className="chart-empty-overlay">
                  No visible series. Select attributes to display.
                </div>
              )}
              <ResponsiveContainer width="100%" height={380}>
              {visualizationType === 'bar' ? (
                <BarChart
                  ref={chartRef}
                  data={isEmptySelection ? [] : displayData}
                  margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
                >
                  {showGrid && <CartesianGrid strokeDasharray="3 3" opacity={0.3} />}
                  
                  <XAxis 
                    dataKey="time" 
                    tick={{fontSize: 12}} 
                    minTickGap={50}
                    scale={xAxisScale === 'log' ? 'log' : xAxisScale === 'symlog' ? 'symlog' : 'linear'}
                    type={xAxisScale === 'log' ? 'number' : undefined}
                    domain={xAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.x || ['auto', 'auto'])}
                    allowDataOverflow={xAxisScale === 'log'}
                  />
                  <YAxis 
                    yAxisId="left" 
                    tick={{fontSize: 12}} 
                    scale={yAxisScale === 'log' ? 'log' : yAxisScale === 'symlog' ? 'symlog' : 'linear'}
                    type={yAxisScale === 'log' ? 'number' : undefined}
                    domain={yAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.y || ['auto', 'auto'])}
                    allowDataOverflow={yAxisScale === 'log'}
                  />
                  {hasRightAxis && (
                    <YAxis 
                      yAxisId="right" 
                      orientation="right" 
                      tick={{fontSize: 12}}
                      scale={yAxisScale === 'log' ? 'log' : yAxisScale === 'symlog' ? 'symlog' : 'linear'}
                      type={yAxisScale === 'log' ? 'number' : undefined}
                      domain={yAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.y || ['auto', 'auto'])}
                      allowDataOverflow={yAxisScale === 'log'}
                    />
                  )}
                  
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '6px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', fontSize: '11px', padding: '8px' }}
                    labelStyle={{ color: '#6b7280', marginBottom: '0.5rem', fontSize: '11px' }}
                    itemStyle={{ fontSize: '11px', padding: '2px 0' }}
                    active={!isPanning}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                  
                  {visibleAttrs.map((attr) => (
                    <Bar
                      key={attr.name}
                      yAxisId={attr.useRightAxis ? 'right' : 'left'}
                      dataKey={`${component.name}.${attr.name}`}
                      fill={attr.color}
                      name={`${component.name}.${attr.name}${attr.unit ? ` (${attr.unit})` : ''}`}
                    />
                  ))}
                </BarChart>
              ) : (
                <LineChart
                  ref={chartRef}
                  data={isEmptySelection ? [] : displayData}
                  margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
                >
                {showGrid && <CartesianGrid strokeDasharray="3 3" opacity={0.3} />}
                
                <XAxis 
                  dataKey="time" 
                  tick={{fontSize: 12}} 
                  minTickGap={50}
                  scale={xAxisScale === 'log' ? 'log' : xAxisScale === 'symlog' ? 'symlog' : 'linear'}
                  type={xAxisScale === 'log' ? 'number' : undefined}
                  domain={xAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.x || ['auto', 'auto'])}
                  allowDataOverflow={xAxisScale === 'log'}
                />
                <YAxis 
                  yAxisId="left" 
                  tick={{fontSize: 12}} 
                  scale={yAxisScale === 'log' ? 'log' : yAxisScale === 'symlog' ? 'symlog' : 'linear'}
                  type={yAxisScale === 'log' ? 'number' : undefined}
                  domain={yAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.y || ['auto', 'auto'])}
                  allowDataOverflow={yAxisScale === 'log'}
                />
                {hasRightAxis && (
                  <YAxis 
                    yAxisId="right" 
                    orientation="right" 
                    tick={{fontSize: 12}}
                    scale={yAxisScale === 'log' ? 'log' : yAxisScale === 'symlog' ? 'symlog' : 'linear'}
                    type={yAxisScale === 'log' ? 'number' : undefined}
                    domain={yAxisScale === 'log' ? [0.01, 'auto'] : (zoomDomain?.y || ['auto', 'auto'])}
                    allowDataOverflow={yAxisScale === 'log'}
                  />
                )}
                
                <Tooltip 
                  contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', borderRadius: '6px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', fontSize: '11px', padding: '8px' }}
                  labelStyle={{ color: '#6b7280', marginBottom: '0.5rem', fontSize: '11px' }}
                  itemStyle={{ fontSize: '11px', padding: '2px 0' }}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }}/>
                
                {/* Visible attributes from selected component */}
                {visibleAttrs.map((attr) => {
                  const showDots = dataDisplay === 'point' || dataDisplay === 'both';
                  const showLine = dataDisplay === 'line' || dataDisplay === 'both';
                  
                  return (
                    <Line
                      key={attr.name}
                      yAxisId={attr.useRightAxis ? 'right' : 'left'}
                      type="monotone"
                      dataKey={`${component.name}.${attr.name}`}
                      stroke={showLine ? attr.color : 'none'}
                      strokeWidth={2}
                      dot={showDots ? { r: 2, fill: attr.color } : false}
                      activeDot={{ r: 6 }}
                      connectNulls={true}
                      isAnimationActive={false}
                      name={`${component.name}.${attr.name}${attr.unit ? ` (${attr.unit})` : ''}`}
                    />
                  );
                })}

                {/* Pinned series */}
                {pinnedSeries.map((pinned) => {
                  const key = `[PINNED] ${pinned.entityName}.${pinned.attributeName}`;
                  const comp = components.find((c) => c.name === pinned.entityName);
                  const attr = comp?.attributes.find((a) => a.name === pinned.attributeName);
                  const showDots = dataDisplay === 'point' || dataDisplay === 'both';
                  const showLine = dataDisplay === 'line' || dataDisplay === 'both';
                  return (
                    <Line
                      key={key}
                      yAxisId={attr?.useRightAxis ? 'right' : 'left'}
                      type="monotone"
                      dataKey={key}
                      stroke={showLine ? pinned.color : 'none'}
                      strokeWidth={2}
                      strokeDasharray={showLine ? "5 5" : undefined}
                      dot={showDots ? { r: 2, fill: pinned.color } : false}
                      activeDot={{ r: 6 }}
                      connectNulls={true}
                      isAnimationActive={false}
                      name={`[PINNED] ${pinned.entityName}.${pinned.attributeName}${pinned.unit ? ` (${pinned.unit})` : ''}`}
                    />
                  );
                })}
                </LineChart>
              )}
            </ResponsiveContainer>
            </div>
            
            {/* Series Selector Panel - Right Side */}
            <div className="series-selector-panel">
              <h4 className="series-panel-title">Display</h4>
              <div className="series-list-vertical">
                {component.attributes.map((attr) => (
                  <div key={attr.name} className="series-item-vertical">
                    <input
                      type="checkbox"
                      id={`series-${attr.name}`}
                      checked={visibleAttributes.has(attr.name)}
                      onChange={() => toggleAttributeVisibility(attr.name)}
                      className="series-checkbox-vertical"
                    />
                    <label htmlFor={`series-${attr.name}`} className="series-label-vertical">
                      <span
                        className="series-color-vertical"
                        style={{ backgroundColor: attr.color }}
                      />
                      <span className="series-name-vertical">
                        {attr.name}
                        {attr.unit && <span className="series-unit-vertical"> ({attr.unit})</span>}
                      </span>
                    </label>
                    <button
                      className={`pin-btn-vertical ${isPinned(component.name, attr.name) ? 'pinned' : ''}`}
                      onClick={() => pinSeries(component.name, attr.name)}
                      disabled={isPinned(component.name, attr.name)}
                      title={isPinned(component.name, attr.name) ? 'Already pinned' : 'Pin for comparison'}
                    >
                      <img src={pinListIcon} alt="Pin" className="pin-icon" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        </div>
      </div>
    );
  };

  const renderStatsTable = (component: ComponentData) => {
    return (
      <div className="stats-table-section">
        <h3 className="stats-section-title">Statistics</h3>
        <div className="stats-table">
          <table>
            <thead>
              <tr>
                <th>Dataset</th>
                <th>Unit</th>
                <th>Min</th>
                <th>Max</th>
                <th>Mean</th>
                <th>Std Dev</th>
              </tr>
            </thead>
            <tbody>
              {component.attributes.map((attr, index) => {
                const values = attr.values;
                const min = Math.min(...values);
                const max = Math.max(...values);
                const mean = values.reduce((a, b) => a + b, 0) / values.length;
                const variance =
                  values.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / values.length;
                const stdDev = Math.sqrt(variance);

                return (
                  <tr key={index}>
                    <td>{attr.name}</td>
                    <td>{attr.unit || '—'}</td>
                    <td>{min.toFixed(3)}</td>
                    <td>{max.toFixed(3)}</td>
                    <td>{mean.toFixed(3)}</td>
                    <td>{stdDev.toFixed(3)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  };


  if (error && !hdf5Files.length) {
    return (
      <div className="results-container">
        <div className="results-error">
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (hdf5Files.length === 0 && !selectedFile) {
    return (
      <div className="results-container">
        <div className="results-empty">
          <p>No results available for this simulation.</p>
        </div>
      </div>
    );
  }

  const selectedCategoryGroup = categoryGroups.find((g) => g.category === selectedCategory);
  const selectedComponentData = components.find((c) => c.name === selectedEntity);

  return (
    <div className="results-container">
      {/* Top Drawer */}
      <div className="drawer-wrapper">
        <div className={`results-drawer ${drawerOpen ? 'open' : ''}`}>
          {drawerOpen && (
            <div className="drawer-content">
              {/* Category Tabs */}
              {categoryGroups.length > 0 && (
                <div className="category-tabs">
                  {categoryGroups.map((group) => (
                    <button
                      key={group.category}
                      className={`category-tab ${selectedCategory === group.category ? 'active' : ''}`}
                      onClick={() => setSelectedCategory(group.category)}
                    >
                      {group.category.charAt(0).toUpperCase() + group.category.slice(1)} ({group.entities.length})
                    </button>
                  ))}
                </div>
              )}

              {/* Entity List for Selected Category */}
              {selectedCategoryGroup && (
                <div className="entity-list">
                  {selectedCategoryGroup.entities.map((entity) => (
                    <button
                      key={entity.name}
                      className={`entity-item ${selectedEntity === entity.name ? 'active' : ''}`}
                      onClick={() => setSelectedEntity(entity.name)}
                    >
                      {entity.name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div
          className="drawer-toggle-tab"
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            setDrawerOpen(!drawerOpen);
          }}
          onMouseDown={(e) => {
            e.preventDefault();
          }}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              setDrawerOpen(!drawerOpen);
            }
          }}
          aria-label={drawerOpen ? 'Close drawer' : 'Open drawer'}
        >
          {drawerOpen ? '▲' : '▼'}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="results-main-content">
        {loading && (
          <div className="results-loading">
            <div className="spinner" />
            <p>Loading results...</p>
          </div>
        )}

        {error && (
          <div className="results-error">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && selectedComponentData && (
          <div className="results-content">
            {renderChart(selectedComponentData)}
            {renderStatsTable(selectedComponentData)}
          </div>
        )}
      </div>
    </div>
  );
};

export default SimulationResults;
