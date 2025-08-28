import React, { useState, useEffect } from 'react';
import * as XLSX from 'xlsx';
import { useToast } from '../../hooks/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { 
  Upload, Database, Calculator, Settings, Save, RefreshCw, 
  Edit, Trash2, Plus, Download, Eye, EyeOff, RotateCcw, 
  DollarSign, FileText, AlertCircle, CheckCircle
} from 'lucide-react';
import { formatCurrency } from '../../utils/helpers';

const CatalystDatabase = () => {
  const [activeSubTab, setActiveSubTab] = useState('data');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Data Tab State
  const [catalystData, setCatalystData] = useState([]);
  const [editingRow, setEditingRow] = useState(null);
  const [editData, setEditData] = useState({});

  // Price Calculations Tab State
  const [priceCalculations, setPriceCalculations] = useState([]);
  const [showOverrideModal, setShowOverrideModal] = useState(false);
  const [overrideItem, setOverrideItem] = useState(null);
  const [overridePrice, setOverridePrice] = useState('');

  // Basis Tab State
  const [basisData, setBasisData] = useState({
    pt_price: 950.00,        // $/toz
    pd_price: 1200.00,       // $/toz
    rh_price: 4500.00,       // $/toz
    exchange_rate: 0.92,     // EUR/USD
    renumeration_pt: 0.95,   // 95%
    renumeration_pd: 0.94,   // 94%
    renumeration_rh: 0.93    // 93%
  });

  useEffect(() => {
    loadCatalystData();
    loadBasisData();
  }, []);

  useEffect(() => {
    // Recalculate prices when basis data changes
    if (catalystData.length > 0) {
      calculateAllPrices();
    }
  }, [basisData, catalystData]);

  // Load catalyst data from backend
  const loadCatalystData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst-data`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCatalystData(data || []);
      }
    } catch (error) {
      console.error('Error loading catalyst data:', error);
      // Initialize with sample data for demo
      setCatalystData([
        {
          id: 1,
          cat_id: 'CAT001',
          pt_ppm: 1250,
          pd_ppm: 800,
          rh_ppm: 150,
          ceramic_weight: 2.5,
          add_info: 'Additional technical details',
          name: 'Standard Ceramic Catalyst'
        },
        {
          id: 2,
          cat_id: 'CAT002', 
          pt_ppm: 980,
          pd_ppm: 650,
          rh_ppm: 120,
          ceramic_weight: 3.2,
          add_info: 'High performance variant',
          name: 'Performance Ceramic Catalyst'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Load basis data from backend
  const loadBasisData = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst-basis`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setBasisData(prev => ({ ...prev, ...data }));
      }
    } catch (error) {
      console.error('Error loading basis data:', error);
    }
  };

  // Calculate total price for a catalyst item
  const calculatePrice = (item) => {
    const { pt_ppm, pd_ppm, rh_ppm, ceramic_weight } = item;
    const { pt_price, pd_price, rh_price, exchange_rate, renumeration_pt, renumeration_pd, renumeration_rh } = basisData;

    // Convert ppm to grams per troy ounce
    const pt_grams = (pt_ppm / 1000000) * ceramic_weight * 31.1035; // Troy ounce to grams
    const pd_grams = (pd_ppm / 1000000) * ceramic_weight * 31.1035;
    const rh_grams = (rh_ppm / 1000000) * ceramic_weight * 31.1035;

    // Convert grams to troy ounces
    const pt_oz = pt_grams / 31.1035;
    const pd_oz = pd_grams / 31.1035;
    const rh_oz = rh_grams / 31.1035;

    // Calculate value in USD
    const pt_value = pt_oz * pt_price * renumeration_pt;
    const pd_value = pd_oz * pd_price * renumeration_pd;
    const rh_value = rh_oz * rh_price * renumeration_rh;

    // Total value in EUR
    const total_usd = pt_value + pd_value + rh_value;
    const total_eur = total_usd * exchange_rate;

    return total_eur;
  };

  // Calculate all prices
  const calculateAllPrices = () => {
    const calculations = catalystData.map(item => ({
      id: item.id,
      cat_id: item.cat_id,
      name: item.name,
      total_price: calculatePrice(item),
      is_overridden: false,
      override_price: null
    }));
    
    setPriceCalculations(calculations);
  };

  // Handle Excel file upload
  const handleExcelUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      setLoading(true);
      
      // Read Excel file
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheetName = workbook.SheetNames[0];
      const worksheet = workbook.Sheets[sheetName];
      const jsonData = XLSX.utils.sheet_to_json(worksheet);

      // Validate required columns
      const requiredColumns = ['cat_id', 'pt_ppm', 'pd_ppm', 'rh_ppm', 'ceramic_weight', 'name'];
      const firstRow = jsonData[0] || {};
      const missingColumns = requiredColumns.filter(col => !(col in firstRow));
      
      if (missingColumns.length > 0) {
        toast({
          title: "Invalid Excel Format",
          description: `Missing columns: ${missingColumns.join(', ')}`,
          variant: "destructive"
        });
        return;
      }

      // Process data
      const processedData = jsonData.map((row, index) => ({
        id: Date.now() + index,
        cat_id: row.cat_id,
        pt_ppm: parseFloat(row.pt_ppm) || 0,
        pd_ppm: parseFloat(row.pd_ppm) || 0,
        rh_ppm: parseFloat(row.rh_ppm) || 0,
        ceramic_weight: parseFloat(row.ceramic_weight) || 0,
        add_info: row.add_info || '',
        name: row.name || `Catalyst ${row.cat_id}`
      }));

      // Save to backend
      await saveCatalystData(processedData);
      
      setCatalystData(processedData);
      
      toast({
        title: "Upload Successful",
        description: `Imported ${processedData.length} catalyst records`
      });
      
    } catch (error) {
      console.error('Error uploading Excel file:', error);
      toast({
        title: "Upload Failed",
        description: "Please check your file format and try again",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Save catalyst data to backend
  const saveCatalystData = async (data) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst-data`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ data })
      });

      if (!response.ok) {
        throw new Error('Failed to save catalyst data');
      }
    } catch (error) {
      console.error('Error saving catalyst data:', error);
      throw error;
    }
  };

  // Save basis data to backend
  const saveBasisData = async () => {
    try {
      setLoading(true);
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/catalyst-basis`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(basisData)
      });

      if (response.ok) {
        toast({
          title: "Basis Data Saved",
          description: "Price calculation variables updated successfully"
        });
      } else {
        throw new Error('Failed to save basis data');
      }
    } catch (error) {
      console.error('Error saving basis data:', error);
      toast({
        title: "Save Failed",
        description: "Failed to save basis data",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle row edit
  const handleRowEdit = (item) => {
    setEditingRow(item.id);
    setEditData({ ...item });
  };

  // Save row edit
  const saveRowEdit = async () => {
    try {
      const updatedData = catalystData.map(item => 
        item.id === editingRow ? { ...editData } : item
      );
      
      await saveCatalystData(updatedData);
      setCatalystData(updatedData);
      setEditingRow(null);
      setEditData({});
      
      toast({
        title: "Row Updated",
        description: "Catalyst data updated successfully"
      });
    } catch (error) {
      toast({
        title: "Update Failed",
        description: "Failed to update catalyst data",
        variant: "destructive"
      });
    }
  };

  // Handle price override
  const handlePriceOverride = (item) => {
    setOverrideItem(item);
    setOverridePrice(item.override_price || item.total_price.toFixed(2));
    setShowOverrideModal(true);
  };

  // Save price override
  const savePriceOverride = () => {
    const updatedCalculations = priceCalculations.map(calc => 
      calc.id === overrideItem.id 
        ? { 
            ...calc, 
            override_price: parseFloat(overridePrice),
            is_overridden: true 
          }
        : calc
    );
    
    setPriceCalculations(updatedCalculations);
    setShowOverrideModal(false);
    setOverrideItem(null);
    
    toast({
      title: "Price Override Applied",
      description: "Custom price has been set"
    });
  };

  // Reset price to calculation
  const resetPrice = (itemId) => {
    const updatedCalculations = priceCalculations.map(calc => 
      calc.id === itemId 
        ? { 
            ...calc, 
            override_price: null,
            is_overridden: false 
          }
        : calc
    );
    
    setPriceCalculations(updatedCalculations);
    
    toast({
      title: "Price Reset",
      description: "Price restored to calculated value"
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-slate-900">Catalyst Database System</h2>
          <p className="text-slate-600">Manage catalyst data, price calculations, and basis variables</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-slate-600">
            {catalystData.length} Records
          </Badge>
          <Badge variant="outline" className="text-slate-600">
            {priceCalculations.length} Calculations
          </Badge>
        </div>
      </div>

      {/* Sub-tabs */}
      <Tabs value={activeSubTab} onValueChange={setActiveSubTab}>
        <TabsList className="grid w-full grid-cols-3 bg-white shadow-sm">
          <TabsTrigger value="data" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Data
          </TabsTrigger>
          <TabsTrigger value="calculations" className="flex items-center gap-2">
            <Calculator className="h-4 w-4" />
            Price Calculations
          </TabsTrigger>
          <TabsTrigger value="basis" className="flex items-center gap-2">
            <Settings className="h-4 w-4" />
            Basis
          </TabsTrigger>
        </TabsList>

        {/* Data Tab */}
        <TabsContent value="data">
          <Card className="border-0 shadow-sm bg-white">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-purple-600" />
                  Catalyst Data Management
                </CardTitle>
                <div className="flex items-center gap-2">
                  <input
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleExcelUpload}
                    className="hidden"
                    id="excel-upload"
                  />
                  <Button
                    onClick={() => document.getElementById('excel-upload')?.click()}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                    disabled={loading}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Excel
                  </Button>
                  <Button
                    onClick={loadCatalystData}
                    variant="outline"
                    disabled={loading}
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                    Refresh
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Data Table */}
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-slate-200">
                  <thead>
                    <tr className="bg-slate-50">
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Cat ID</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Pt PPM</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Pd PPM</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Rh PPM</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Ceramic Weight</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Name</th>
                      <th className="border border-slate-200 px-4 py-2 text-left text-sm font-medium text-slate-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {catalystData.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50">
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              value={editData.cat_id || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, cat_id: e.target.value }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.cat_id}</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              type="number"
                              value={editData.pt_ppm || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, pt_ppm: parseFloat(e.target.value) }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.pt_ppm}</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              type="number"
                              value={editData.pd_ppm || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, pd_ppm: parseFloat(e.target.value) }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.pd_ppm}</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              type="number"
                              value={editData.rh_ppm || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, rh_ppm: parseFloat(e.target.value) }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.rh_ppm}</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              type="number"
                              step="0.1"
                              value={editData.ceramic_weight || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, ceramic_weight: parseFloat(e.target.value) }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.ceramic_weight}g</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          {editingRow === item.id ? (
                            <Input
                              value={editData.name || ''}
                              onChange={(e) => setEditData(prev => ({ ...prev, name: e.target.value }))}
                              className="h-8 text-sm"
                            />
                          ) : (
                            <span className="text-sm">{item.name}</span>
                          )}
                        </td>
                        <td className="border border-slate-200 px-4 py-2">
                          <div className="flex items-center gap-1">
                            {editingRow === item.id ? (
                              <>
                                <Button
                                  onClick={saveRowEdit}
                                  size="sm"
                                  className="h-7 px-2 text-xs bg-green-600 hover:bg-green-700"
                                >
                                  <Save className="h-3 w-3" />
                                </Button>
                                <Button
                                  onClick={() => {
                                    setEditingRow(null);
                                    setEditData({});
                                  }}
                                  size="sm"
                                  variant="outline"
                                  className="h-7 px-2 text-xs"
                                >
                                  Cancel
                                </Button>
                              </>
                            ) : (
                              <Button
                                onClick={() => handleRowEdit(item)}
                                size="sm"
                                variant="outline"
                                className="h-7 px-2 text-xs"
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {catalystData.length === 0 && (
                <div className="text-center py-12">
                  <Database className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No Catalyst Data</h3>
                  <p className="text-slate-600 mb-4">Upload an Excel file to get started</p>
                  <Button
                    onClick={() => document.getElementById('excel-upload')?.click()}
                    className="bg-purple-600 hover:bg-purple-700 text-white"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Excel File
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Price Calculations Tab */}
        <TabsContent value="calculations">
          <Card className="border-0 shadow-sm bg-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="h-5 w-5 text-purple-600" />
                Price Calculations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {priceCalculations.map((calc) => (
                  <div key={calc.id} className="flex items-center justify-between p-4 border border-slate-200 rounded-lg">
                    <div>
                      <div className="flex items-center gap-3">
                        <h4 className="font-semibold text-slate-900">{calc.name}</h4>
                        <Badge variant="outline" className="text-xs">{calc.cat_id}</Badge>
                        {calc.is_overridden && (
                          <Badge className="text-xs bg-orange-100 text-orange-800">Overridden</Badge>
                        )}
                      </div>
                      <div className="mt-2">
                        <span className="text-2xl font-bold text-purple-600">
                          {calc.is_overridden 
                            ? formatCurrency(calc.override_price) 
                            : formatCurrency(calc.total_price)
                          }
                        </span>
                        {calc.is_overridden && (
                          <span className="ml-2 text-sm text-slate-500 line-through">
                            {formatCurrency(calc.total_price)}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        onClick={() => resetPrice(calc.id)}
                        size="sm"
                        variant="outline"
                        className="text-green-600 border-green-200 hover:bg-green-50"
                      >
                        <RotateCcw className="h-4 w-4 mr-1" />
                        Reset
                      </Button>
                      <Button
                        onClick={() => handlePriceOverride(calc)}
                        size="sm"
                        className="bg-orange-600 hover:bg-orange-700 text-white"
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Override
                      </Button>
                    </div>
                  </div>
                ))}
              </div>

              {priceCalculations.length === 0 && (
                <div className="text-center py-12">
                  <Calculator className="h-16 w-16 mx-auto text-slate-400 mb-4" />
                  <h3 className="text-lg font-semibold text-slate-900 mb-2">No Price Calculations</h3>
                  <p className="text-slate-600">Upload catalyst data first to see price calculations</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Basis Tab */}
        <TabsContent value="basis">
          <Card className="border-0 shadow-sm bg-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-purple-600" />
                Basis Variables
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Metal Prices */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-900">Metal Prices ($/toz)</h3>
                  
                  <div>
                    <Label className="text-slate-700">Platinum Price</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <DollarSign className="h-4 w-4 text-slate-400" />
                      <Input
                        type="number"
                        step="0.01"
                        value={basisData.pt_price}
                        onChange={(e) => setBasisData(prev => ({ ...prev, pt_price: parseFloat(e.target.value) }))}
                        className="flex-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label className="text-slate-700">Palladium Price</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <DollarSign className="h-4 w-4 text-slate-400" />
                      <Input
                        type="number"
                        step="0.01"
                        value={basisData.pd_price}
                        onChange={(e) => setBasisData(prev => ({ ...prev, pd_price: parseFloat(e.target.value) }))}
                        className="flex-1"
                      />
                    </div>
                  </div>

                  <div>
                    <Label className="text-slate-700">Rhodium Price</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <DollarSign className="h-4 w-4 text-slate-400" />
                      <Input
                        type="number"
                        step="0.01"
                        value={basisData.rh_price}
                        onChange={(e) => setBasisData(prev => ({ ...prev, rh_price: parseFloat(e.target.value) }))}
                        className="flex-1"
                      />
                    </div>
                  </div>
                </div>

                {/* Exchange Rate */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-900">Exchange Rate</h3>
                  
                  <div>
                    <Label className="text-slate-700">EUR/USD Rate</Label>
                    <Input
                      type="number"
                      step="0.001"
                      value={basisData.exchange_rate}
                      onChange={(e) => setBasisData(prev => ({ ...prev, exchange_rate: parseFloat(e.target.value) }))}
                      className="mt-1"
                    />
                  </div>
                </div>

                {/* Renumeration */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-900">Renumeration (%)</h3>
                  
                  <div>
                    <Label className="text-slate-700">Platinum Renumeration</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={basisData.renumeration_pt}
                      onChange={(e) => setBasisData(prev => ({ ...prev, renumeration_pt: parseFloat(e.target.value) }))}
                      className="mt-1"
                    />
                    <p className="text-xs text-slate-500 mt-1">{(basisData.renumeration_pt * 100).toFixed(1)}%</p>
                  </div>

                  <div>
                    <Label className="text-slate-700">Palladium Renumeration</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={basisData.renumeration_pd}
                      onChange={(e) => setBasisData(prev => ({ ...prev, renumeration_pd: parseFloat(e.target.value) }))}
                      className="mt-1"
                    />
                    <p className="text-xs text-slate-500 mt-1">{(basisData.renumeration_pd * 100).toFixed(1)}%</p>
                  </div>

                  <div>
                    <Label className="text-slate-700">Rhodium Renumeration</Label>
                    <Input
                      type="number"
                      step="0.01"
                      min="0"
                      max="1"
                      value={basisData.renumeration_rh}
                      onChange={(e) => setBasisData(prev => ({ ...prev, renumeration_rh: parseFloat(e.target.value) }))}
                      className="mt-1"
                    />
                    <p className="text-xs text-slate-500 mt-1">{(basisData.renumeration_rh * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end mt-8">
                <Button
                  onClick={saveBasisData}
                  className="bg-purple-600 hover:bg-purple-700 text-white"
                  disabled={loading}
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save Basis Data
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Price Override Modal */}
      {showOverrideModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="p-6">
              <h3 className="text-xl font-bold text-slate-900 mb-4">Override Price</h3>
              <p className="text-slate-600 mb-4">
                Set a custom price for <strong>{overrideItem?.name}</strong>
              </p>
              
              <div className="space-y-4">
                <div>
                  <Label>Calculated Price</Label>
                  <div className="text-lg text-slate-600">
                    {formatCurrency(overrideItem?.total_price)}
                  </div>
                </div>
                
                <div>
                  <Label>Override Price (EUR)</Label>
                  <Input
                    type="number"
                    step="0.01"
                    value={overridePrice}
                    onChange={(e) => setOverridePrice(e.target.value)}
                    className="mt-1"
                    placeholder="Enter custom price"
                  />
                </div>
              </div>
              
              <div className="flex gap-3 mt-6">
                <Button
                  onClick={savePriceOverride}
                  className="flex-1 bg-orange-600 hover:bg-orange-700 text-white"
                >
                  Apply Override
                </Button>
                <Button
                  onClick={() => setShowOverrideModal(false)}
                  variant="outline"
                  className="flex-1"
                >
                  Cancel
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CatalystDatabase;