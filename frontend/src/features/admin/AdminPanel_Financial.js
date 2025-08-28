{/* Financial Management Pro Tab */}
          <TabsContent value="financial">
            <div className="space-y-6">
              {/* Financial Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card className="border-0 shadow-sm bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-emerald-100 text-sm">Total Revenue</p>
                        <p className="text-3xl font-bold">{formatCurrency(stats.total_revenue || 0)}</p>
                        <p className="text-emerald-200 text-xs">+12.3% from last month</p>
                      </div>
                      <DollarSign className="h-8 w-8 text-emerald-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-100 text-sm">Commissions Earned</p>
                        <p className="text-3xl font-bold">{formatCurrency((stats.total_revenue || 0) * 0.05)}</p>
                        <p className="text-blue-200 text-xs">5% commission rate</p>
                      </div>
                      <PieChart className="h-8 w-8 text-blue-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-orange-100 text-sm">Pending Payouts</p>
                        <p className="text-3xl font-bold">{formatCurrency((stats.total_revenue || 0) * 0.15)}</p>
                        <p className="text-orange-200 text-xs">24 sellers waiting</p>
                      </div>
                      <Clock className="h-8 w-8 text-orange-200" />
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-purple-100 text-sm">Monthly Growth</p>
                        <p className="text-3xl font-bold">+{(Math.random() * 20 + 5).toFixed(1)}%</p>
                        <p className="text-purple-200 text-xs">Revenue growth</p>
                      </div>
                      <TrendingUp className="h-8 w-8 text-purple-200" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Revenue Analytics & Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <BarChart3 className="h-5 w-5 text-purple-600" />
                      Revenue Trends (30 Days)
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {Array.from({length: 7}, (_, i) => {
                        const date = new Date();
                        date.setDate(date.getDate() - (6 - i));
                        const revenue = Math.random() * 3000 + 1000;
                        const orders = Math.floor(Math.random() * 25) + 5;
                        
                        return (
                          <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                              <span className="text-sm text-slate-600">{date.toLocaleDateString()}</span>
                            </div>
                            <div className="text-right">
                              <div className="font-semibold text-slate-900">{formatCurrency(revenue)}</div>
                              <div className="text-xs text-slate-500">{orders} orders</div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <PieChart className="h-5 w-5 text-purple-600" />
                      Commission Breakdown
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {[
                        {category: 'Electronics', percentage: 35, amount: (stats.total_revenue || 0) * 0.35 * 0.05},
                        {category: 'Fashion', percentage: 28, amount: (stats.total_revenue || 0) * 0.28 * 0.05},
                        {category: 'Home & Garden', percentage: 20, amount: (stats.total_revenue || 0) * 0.20 * 0.05},
                        {category: 'Sports', percentage: 17, amount: (stats.total_revenue || 0) * 0.17 * 0.05}
                      ].map((item, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded ${
                              index === 0 ? 'bg-purple-500' : 
                              index === 1 ? 'bg-blue-500' : 
                              index === 2 ? 'bg-green-500' : 'bg-orange-500'
                            }`}></div>
                            <span className="text-sm font-medium text-slate-900">{item.category}</span>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold text-slate-900">{formatCurrency(item.amount)}</div>
                            <div className="text-xs text-slate-500">{item.percentage}% of commissions</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Financial Tools & Management */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <DollarSign className="h-5 w-5 text-purple-600" />
                      Commission & Fee Management
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-slate-700">Base Commission Rate (%)</Label>
                        <Input
                          type="number"
                          placeholder="5.0"
                          className="border-slate-200 mt-2"
                          min="0"
                          max="100"
                          step="0.1"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-700">Payment Processing Fee (%)</Label>
                        <Input
                          type="number"
                          placeholder="2.9"
                          className="border-slate-200 mt-2"
                          min="0"
                          max="10"
                          step="0.1"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-slate-700">Listing Fee</Label>
                        <Input
                          type="number"
                          placeholder="0.50"
                          className="border-slate-200 mt-2"
                          min="0"
                          step="0.01"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-700">Featured Listing Fee</Label>
                        <Input
                          type="number"
                          placeholder="5.00"
                          className="border-slate-200 mt-2"
                          min="0"
                          step="0.01"
                        />
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-slate-700">Progressive Commission Tiers</Label>
                        <Switch />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label className="text-slate-700">Auto-adjust for High Volume Sellers</Label>
                        <Switch />
                      </div>
                    </div>

                    <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">
                      <Save className="h-4 w-4 mr-2" />
                      Save Commission Settings
                    </Button>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-sm bg-white">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <RefreshCw className="h-5 w-5 text-purple-600" />
                      Payout Management
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 gap-4">
                      <div>
                        <Label className="text-slate-700">Payout Schedule</Label>
                        <select className="w-full px-3 py-2 border border-slate-200 rounded-md text-sm bg-white mt-2">
                          <option value="weekly">Weekly (Every Friday)</option>
                          <option value="biweekly">Bi-weekly</option>
                          <option value="monthly">Monthly (1st of month)</option>
                          <option value="manual">Manual Approval</option>
                        </select>
                      </div>
                      
                      <div>
                        <Label className="text-slate-700">Minimum Payout Amount</Label>
                        <Input
                          type="number"
                          placeholder="25.00"
                          className="border-slate-200 mt-2"
                          min="1"
                          step="0.01"
                        />
                      </div>
                      
                      <div>
                        <Label className="text-slate-700">Hold Period (Days)</Label>
                        <Input
                          type="number"
                          placeholder="7"
                          className="border-slate-200 mt-2"
                          min="0"
                          max="30"
                        />
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <Label className="text-slate-700">Auto-process Payouts</Label>
                        <Switch defaultChecked />
                      </div>
                      <div className="flex items-center justify-between">
                        <Label className="text-slate-700">Email Notifications</Label>
                        <Switch defaultChecked />
                      </div>
                    </div>

                    <div className="flex gap-2 pt-2">
                      <Button className="flex-1 bg-green-600 hover:bg-green-700 text-white">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Process Payouts
                      </Button>
                      <Button variant="outline" className="flex-1">
                        <Eye className="h-4 w-4 mr-2" />
                        View Queue
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Transaction History & Reports */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-slate-900">
                      <Activity className="h-5 w-5 text-purple-600" />
                      Financial Transaction History
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export CSV
                      </Button>
                      <Button variant="outline" size="sm">
                        <Filter className="h-4 w-4 mr-2" />
                        Filter
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full border-collapse">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="text-left p-3 font-medium text-slate-700">Transaction ID</th>
                          <th className="text-left p-3 font-medium text-slate-700">Type</th>
                          <th className="text-left p-3 font-medium text-slate-700">User</th>
                          <th className="text-left p-3 font-medium text-slate-700">Amount</th>
                          <th className="text-left p-3 font-medium text-slate-700">Commission</th>
                          <th className="text-left p-3 font-medium text-slate-700">Status</th>
                          <th className="text-left p-3 font-medium text-slate-700">Date</th>
                          <th className="text-left p-3 font-medium text-slate-700">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Array.from({length: 10}, (_, i) => {
                          const transactionTypes = ['Sale', 'Payout', 'Refund', 'Commission', 'Fee'];
                          const statuses = ['Completed', 'Pending', 'Failed', 'Processing'];
                          const type = transactionTypes[Math.floor(Math.random() * transactionTypes.length)];
                          const status = statuses[Math.floor(Math.random() * statuses.length)];
                          const amount = Math.random() * 500 + 10;
                          const commission = type === 'Sale' ? amount * 0.05 : 0;
                          
                          return (
                            <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                              <td className="p-3">
                                <span className="font-mono text-sm text-purple-600">#{`TXN${(1000 + i).toString().padStart(6, '0')}`}</span>
                              </td>
                              <td className="p-3">
                                <Badge variant="outline" className="text-xs">
                                  {type}
                                </Badge>
                              </td>
                              <td className="p-3">
                                <span className="text-sm text-slate-900">User {Math.floor(Math.random() * 100) + 1}</span>
                              </td>
                              <td className="p-3">
                                <span className="font-medium text-slate-900">{formatCurrency(amount)}</span>
                              </td>
                              <td className="p-3">
                                <span className="text-sm text-slate-600">{formatCurrency(commission)}</span>
                              </td>
                              <td className="p-3">
                                <Badge 
                                  variant={status === 'Completed' ? 'default' : 'outline'}
                                  className={`text-xs ${
                                    status === 'Completed' ? 'bg-green-600' : 
                                    status === 'Pending' ? 'bg-orange-600' : 
                                    status === 'Processing' ? 'bg-blue-600' :
                                    'bg-red-600'
                                  }`}
                                >
                                  {status}
                                </Badge>
                              </td>
                              <td className="p-3">
                                <span className="text-sm text-slate-600">
                                  {new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}
                                </span>
                              </td>
                              <td className="p-3">
                                <div className="flex items-center gap-2">
                                  <Button variant="outline" size="sm">
                                    <Eye className="h-3 w-3" />
                                  </Button>
                                  <Button variant="outline" size="sm">
                                    <Download className="h-3 w-3" />
                                  </Button>
                                </div>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>

              {/* Tax & Compliance Tools */}
              <Card className="border-0 shadow-sm bg-white">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-slate-900">
                    <Shield className="h-5 w-5 text-purple-600" />
                    Tax & Compliance Management
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <Label className="text-slate-700">Tax Collection</Label>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-slate-600">Auto-calculate sales tax</span>
                        <Switch defaultChecked />
                      </div>
                    </div>
                    <div>
                      <Label className="text-slate-700">1099 Generation</Label>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-slate-600">Generate tax forms</span>
                        <Switch />
                      </div>
                    </div>
                    <div>
                      <Label className="text-slate-700">VAT/GST Compliance</Label>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-sm text-slate-600">International tax handling</span>
                        <Switch />
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex gap-4 pt-4 border-t border-slate-200">
                    <Button className="bg-purple-600 hover:bg-purple-700 text-white">
                      <Download className="h-4 w-4 mr-2" />
                      Generate Tax Report
                    </Button>
                    <Button variant="outline">
                      <Calendar className="h-4 w-4 mr-2" />
                      Schedule Reports
                    </Button>
                    <Button variant="outline">
                      <Settings className="h-4 w-4 mr-2" />
                      Tax Settings
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>