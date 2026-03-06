import React from 'react'
import { Link } from 'react-router-dom'
import { Layout, Card, Button } from '../components'

const Home: React.FC = () => {
  const features = [
    {
      icon: '📝',
      title: '文字生成脚本',
      description: '智能生成创作脚本，支持问答式完善和直接输入两种模式',
      link: '/create/script',
      color: 'bg-blue-50 hover:bg-blue-100',
    },
    {
      icon: '🖼️',
      title: '图片生成',
      description: 'AI图片生成，支持多种风格、分辨率和参考图上传',
      link: '/create/image',
      color: 'bg-green-50 hover:bg-green-100',
    },
    {
      icon: '🎬',
      title: '视频生成',
      description: 'AI视频生成，支持自定义时长、风格和故事线',
      link: '/create/video',
      color: 'bg-purple-50 hover:bg-purple-100',
    },
    {
      icon: '📢',
      title: '广告设计',
      description: '智能广告创意设计，支持图文广告和视频广告',
      link: '/create/ad',
      color: 'bg-orange-50 hover:bg-orange-100',
    },
  ]

  const stats = [
    { label: '累计用户', value: '10,000+' },
    { label: '生成作品', value: '100,000+' },
    { label: '满意率', value: '98%' },
  ]

  return (
    <Layout>
      <div className="space-y-12">
        <section className="text-center py-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            AI驱动的创作平台
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
            一站式AI创作解决方案，轻松生成脚本、图片、视频和广告创意
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/register">
              <Button size="lg">立即开始</Button>
            </Link>
            <Link to="/gallery">
              <Button variant="secondary" size="lg">浏览作品集</Button>
            </Link>
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <Link key={feature.link} to={feature.link}>
              <Card className={`h-full transition-colors ${feature.color}`}>
                <div className="text-center">
                  <span className="text-5xl mb-4 block">{feature.icon}</span>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 text-sm">{feature.description}</p>
                </div>
              </Card>
            </Link>
          ))}
        </section>

        <section className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">
            平台数据
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-indigo-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-8 text-white">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-2xl font-bold mb-4">灵活的付费方案</h2>
            <p className="mb-6 opacity-90">
              支持按次付费、月度订阅、年度订阅三种模式，满足不同需求
            </p>
            <Link to="/pricing">
              <Button
                variant="secondary"
                size="lg"
                className="bg-white text-indigo-600 hover:bg-gray-100"
              >
                查看价格方案
              </Button>
            </Link>
          </div>
        </section>
      </div>
    </Layout>
  )
}

export default Home
